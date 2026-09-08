import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Sprout } from "lucide-react";
import { PageHeader, StatCard } from "./Common";

describe("PageHeader", () => {
  it("renders the title", () => {
    render(<PageHeader title="My Farms" />);
    expect(screen.getByRole("heading", { name: "My Farms" })).toBeInTheDocument();
  });

  it("renders an optional subtitle", () => {
    render(<PageHeader title="My Farms" subtitle="3 farms under management" />);
    expect(screen.getByText("3 farms under management")).toBeInTheDocument();
  });

  it("omits the subtitle when not provided", () => {
    render(<PageHeader title="My Farms" />);
    expect(screen.queryByText(/farms under management/)).not.toBeInTheDocument();
  });

  it("renders an optional action", () => {
    render(<PageHeader title="My Farms" action={<button>Add Farm</button>} />);
    expect(screen.getByRole("button", { name: "Add Farm" })).toBeInTheDocument();
  });
});

describe("StatCard", () => {
  it("renders the label and value", () => {
    render(<StatCard icon={Sprout} label="Total Farms" value={4} />);
    expect(screen.getByText("Total Farms")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
  });

  it("renders optional sub text when provided", () => {
    render(<StatCard icon={Sprout} label="Current Crops" value={2} sub="Rice, Wheat" />);
    expect(screen.getByText("Rice, Wheat")).toBeInTheDocument();
  });
});
