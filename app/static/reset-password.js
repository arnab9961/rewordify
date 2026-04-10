const resetForm = document.getElementById("resetForm");
const resetStatus = document.getElementById("resetStatus");

function setStatus(message, type = "") {
  resetStatus.textContent = message;
  resetStatus.classList.remove("error");
  if (type) {
    resetStatus.classList.add(type);
  }
}

function getErrorMessage(data, fallback = "Something went wrong.") {
  if (!data) {
    return fallback;
  }
  if (typeof data.detail === "string") {
    return data.detail;
  }
  if (Array.isArray(data.detail) && data.detail.length > 0) {
    const first = data.detail[0];
    const fieldName = Array.isArray(first?.loc) ? String(first.loc[first.loc.length - 1] || "").toLowerCase() : "";
    const rawMessage = String(first?.msg || "");
    if (rawMessage.includes("at least 8 characters") || rawMessage.includes("ensure this value has at least 8 characters")) {
      if (fieldName === "new_password") {
        return "Password should have at least 8 characters.";
      }
    }
    if (rawMessage.includes("field required") || rawMessage.includes("value_error.missing")) {
      if (fieldName === "new_password") {
        return "Password is required.";
      }
      if (fieldName === "confirm_password") {
        return "Please confirm your password.";
      }
    }
    return first?.msg || fallback;
  }
  return fallback;
}

async function handleResetSubmit(event) {
  event.preventDefault();
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");
  const formData = new FormData(resetForm);
  const newPassword = String(formData.get("newPassword") || "");
  const confirmPassword = String(formData.get("confirmPassword") || "");

  if (!token) {
    setStatus("Missing or invalid reset token.", "error");
    return;
  }
  if (newPassword.length < 8) {
    setStatus("Password must be at least 8 characters.", "error");
    return;
  }
  if (newPassword !== confirmPassword) {
    setStatus("Passwords do not match.", "error");
    return;
  }

  setStatus("Updating your password...");
  try {
    const response = await fetch("/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, new_password: newPassword }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(getErrorMessage(data, "Unable to reset password."));
    }
    setStatus("Password reset successful. Redirecting to login...");
    setTimeout(() => {
      window.location.href = "/login";
    }, 1200);
  } catch (error) {
    setStatus(error.message || "Something went wrong.", "error");
  }
}

if (resetForm) {
  resetForm.addEventListener("submit", handleResetSubmit);
}