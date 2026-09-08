import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import FarmPicker from "./FarmPicker";
import { farmApi } from "../services/api";

vi.mock("../services/api", () => ({
  farmApi: { list: vi.fn() },
}));

describe("FarmPicker", () => {
  beforeEach(() => {
    farmApi.list.mockReset();
  });

  it("renders nothing while there are no farms", async () => {
    farmApi.list.mockResolvedValueOnce([]);
    const { container } = render(<FarmPicker value={null} onChange={vi.fn()} />);

    await waitFor(() => expect(farmApi.list).toHaveBeenCalled());
    expect(container).toBeEmptyDOMElement();
  });

  it("lists the user's farms plus an ad-hoc option once loaded", async () => {
    farmApi.list.mockResolvedValueOnce([
      { id: "farm-1", name: "North Field" },
      { id: "farm-2", name: "South Field" },
    ]);
    render(<FarmPicker value={null} onChange={vi.fn()} />);

    expect(await screen.findByText("North Field")).toBeInTheDocument();
    expect(screen.getByText("South Field")).toBeInTheDocument();
    expect(screen.getByText(/ad-hoc calculation/i)).toBeInTheDocument();
  });

  it("calls onChange with the selected farm id", async () => {
    farmApi.list.mockResolvedValueOnce([{ id: "farm-1", name: "North Field" }]);
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<FarmPicker value={null} onChange={onChange} />);

    await screen.findByText("North Field");
    await user.selectOptions(screen.getByRole("combobox"), "farm-1");

    expect(onChange).toHaveBeenCalledWith("farm-1");
  });

  it("silently shows nothing if the farm list request fails", async () => {
    farmApi.list.mockRejectedValueOnce(new Error("network error"));
    const { container } = render(<FarmPicker value={null} onChange={vi.fn()} />);

    await waitFor(() => expect(farmApi.list).toHaveBeenCalled());
    expect(container).toBeEmptyDOMElement();
  });
});
