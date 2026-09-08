import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Loader, ErrorState, EmptyState, SeverityBadge } from "./Feedback";

describe("Loader", () => {
  it("renders the default label", () => {
    render(<Loader />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders a custom label", () => {
    render(<Loader label="Fetching farms..." />);
    expect(screen.getByText("Fetching farms...")).toBeInTheDocument();
  });
});

describe("ErrorState", () => {
  it("renders the error message", () => {
    render(<ErrorState message="Could not load farms." />);
    expect(screen.getByText("Could not load farms.")).toBeInTheDocument();
  });

  it("does not render a retry button when onRetry is not provided", () => {
    render(<ErrorState message="Something broke." />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("calls onRetry when the retry button is clicked", async () => {
    const onRetry = vi.fn();
    const user = userEvent.setup();
    render(<ErrorState message="Something broke." onRetry={onRetry} />);

    await user.click(screen.getByRole("button", { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});

describe("EmptyState", () => {
  it("renders title and message", () => {
    render(<EmptyState title="No farms yet" message="Add your first farm." />);
    expect(screen.getByText("No farms yet")).toBeInTheDocument();
    expect(screen.getByText("Add your first farm.")).toBeInTheDocument();
  });

  it("renders an optional action element", () => {
    render(<EmptyState title="Empty" action={<button>Add Farm</button>} />);
    expect(screen.getByRole("button", { name: "Add Farm" })).toBeInTheDocument();
  });
});

describe("SeverityBadge", () => {
  it.each([
    ["low", "low"],
    ["medium", "medium"],
    ["high", "high"],
    ["info", "info"],
  ])("renders the '%s' severity label", (severity, expected) => {
    render(<SeverityBadge severity={severity} />);
    expect(screen.getByText(expected)).toBeInTheDocument();
  });

  it("falls back to the info style for an unknown severity", () => {
    render(<SeverityBadge severity="unknown-value" />);
    expect(screen.getByText("unknown-value")).toHaveClass("badge-info");
  });
});
