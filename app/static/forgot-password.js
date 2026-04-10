const forgotForm = document.getElementById("forgotForm");
const forgotStatus = document.getElementById("forgotStatus");

function setStatus(message, type = "") {
  forgotStatus.textContent = message;
  forgotStatus.classList.remove("error");
  if (type) {
    forgotStatus.classList.add(type);
  }
}

async function handleForgotSubmit(event) {
  event.preventDefault();
  const formData = new FormData(forgotForm);
  const email = String(formData.get("resetEmail") || "").trim();
  if (!email) {
    setStatus("Please enter your account email.", "error");
    return;
  }

  setStatus("Sending reset link...");
  try {
    const response = await fetch("/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Unable to process password reset.");
    }
    setStatus(data.detail || "If this email exists, a reset link has been sent.");
    forgotForm.reset();
  } catch (error) {
    setStatus(error.message || "Something went wrong.", "error");
  }
}

if (forgotForm) {
  forgotForm.addEventListener("submit", handleForgotSubmit);
}