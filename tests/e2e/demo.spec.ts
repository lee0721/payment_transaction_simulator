import { test, expect } from "@playwright/test";

test.describe("RiskOps demo flow", () => {
  test("submits a transaction and shows stats/audits", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: /Simulate authorization/i }).click();

    const decisionPanel = page.getByTestId("decision-result");
    await expect(decisionPanel).toContainText('"transaction_id"');
    await expect(decisionPanel).toContainText('"status"');

    const auditPanel = page.getByTestId("audit-trail");
    await expect(auditPanel).toContainText('"decision_payload"');

    const statsPanel = page.getByTestId("stats-panel");
    await expect(statsPanel).toContainText('"total"');
  });
});
