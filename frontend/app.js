const API_BASE = window.location.origin;

const paymentForm = document.getElementById("payment-form");
const paymentResult = document.getElementById("payment-result");
const transactionIdInput = document.getElementById("transaction-id");
const lookupForm = document.getElementById("lookup-form");
const transactionResult = document.getElementById("transaction-result");
const statsResult = document.getElementById("stats-result");
const statsRefresh = document.getElementById("stats-refresh");

const renderJSON = (element, data) => {
  element.textContent = JSON.stringify(data, null, 2);
};

const renderError = (element, error) => {
  const message =
    error?.detail ??
    error?.message ??
    "Unexpected error — open the browser console for technical details.";
  renderJSON(element, { error: message });
};

paymentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const cardNumber = document.getElementById("card-number").value.trim();
  const amount = parseFloat(document.getElementById("amount").value);
  const merchant = document.getElementById("merchant").value.trim();

  renderJSON(paymentResult, { status: "Processing..." });

  try {
    const response = await fetch(`${API_BASE}/payment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ card_number: cardNumber, amount, merchant }),
    });
    const data = await response.json();
    if (!response.ok) {
      renderError(paymentResult, data);
      return;
    }

    renderJSON(paymentResult, data);
    transactionIdInput.value = data.transaction_id;
    await refreshStats();
  } catch (error) {
    renderError(paymentResult, error);
  }
});

lookupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = transactionIdInput.value.trim();
  if (!id) {
    renderError(transactionResult, { message: "請先輸入 transaction_id" });
    return;
  }

  renderJSON(transactionResult, { status: "Fetching..." });

  try {
    const response = await fetch(`${API_BASE}/transaction/${encodeURIComponent(id)}`);
    const data = await response.json();
    if (!response.ok) {
      renderError(transactionResult, data);
      return;
    }
    renderJSON(transactionResult, data);
  } catch (error) {
    renderError(transactionResult, error);
  }
});

const refreshStats = async () => {
  renderJSON(statsResult, { status: "Refreshing..." });
  try {
    const response = await fetch(`${API_BASE}/stats`);
    const data = await response.json();
    if (!response.ok) {
      renderError(statsResult, data);
      return;
    }
    renderJSON(statsResult, data);
  } catch (error) {
    renderError(statsResult, error);
  }
};

statsRefresh.addEventListener("click", refreshStats);

// bootstrap view
refreshStats();
