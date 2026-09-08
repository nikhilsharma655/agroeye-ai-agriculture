import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CropRecommendation from "./CropRecommendation";
import { mlApi, farmApi } from "../services/api";

vi.mock("../services/api", () => ({
  mlApi: { recommendCrop: vi.fn() },
  farmApi: { list: vi.fn() },
}));

describe("CropRecommendation page", () => {
  beforeEach(() => {
    mlApi.recommendCrop.mockReset();
    farmApi.list.mockResolvedValue([]);
  });

  it("renders the form with sensible defaults", async () => {
    render(<CropRecommendation />);
    expect(screen.getByRole("heading", { name: /ai crop recommendation/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /get recommendation/i })).toBeInTheDocument();
    await waitFor(() => expect(farmApi.list).toHaveBeenCalled());
  });

  it("submits the form and displays the recommendation result", async () => {
    mlApi.recommendCrop.mockResolvedValueOnce({
      recommended_crop: "rice",
      suitability_score: 92.5,
      top_recommendations: [
        { crop: "rice", confidence: 92.5 },
        { crop: "maize", confidence: 84.0 },
      ],
      explanation: "Rice matches the soil and climate profile closely.",
    });

    const user = userEvent.setup();
    render(<CropRecommendation />);

    await user.click(screen.getByRole("button", { name: /get recommendation/i }));

    await waitFor(() => expect(mlApi.recommendCrop).toHaveBeenCalledTimes(1));
    // "Rice" and its confidence appear in both the highlighted summary and the
    // ranked list below, so assert presence rather than uniqueness.
    expect((await screen.findAllByText("Rice")).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/92\.5%/).length).toBeGreaterThan(0);
    expect(screen.getByText(/matches the soil and climate profile/i)).toBeInTheDocument();
  });

  it("shows an error message when the recommendation request fails", async () => {
    mlApi.recommendCrop.mockRejectedValueOnce(new Error("Crop recommendation model failed"));
    const user = userEvent.setup();
    render(<CropRecommendation />);

    await user.click(screen.getByRole("button", { name: /get recommendation/i }));

    expect(await screen.findByText("Crop recommendation model failed")).toBeInTheDocument();
  });
});
