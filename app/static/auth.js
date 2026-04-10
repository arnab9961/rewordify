const form = document.getElementById("authForm");
const statusEl = document.getElementById("authStatus");
const mode = document.body.dataset.mode;
const otpFieldWrap = document.getElementById("otpFieldWrap");
const otpInput = document.getElementById("otp");
const confirmPasswordInput = document.getElementById("confirmPassword");
let signupOtpStep = false;

function setStatus(message, type = "") {
  statusEl.textContent = message;
  statusEl.classList.remove("error");
  if (type) {
    statusEl.classList.add(type);
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
      if (fieldName === "password" || fieldName === "new_password") {
        return "Password should have at least 8 characters.";
      }
    }
    if (rawMessage.includes("field required") || rawMessage.includes("value_error.missing")) {
      if (fieldName === "password") {
        return "Password is required.";
      }
      if (fieldName === "email") {
        return "Email is required.";
      }
      if (fieldName === "username") {
        return "Username is required.";
      }
      if (fieldName === "otp") {
        return "OTP is required.";
      }
    }
    return first?.msg || fallback;
  }
  return fallback;
}

async function redirectIfLoggedIn() {
  try {
    const response = await fetch("/auth/me");
    if (response.ok) {
      window.location.href = "/";
    }
  } catch {
    // Ignore network issues here.
  }
}

async function handleSubmit(event) {
  event.preventDefault();
  const formData = new FormData(form);
  let payload = Object.fromEntries(formData.entries());
  let endpoint = mode === "signup" ? "/auth/signup" : "/auth/login";

  if (mode === "signup" && !signupOtpStep) {
    const password = String(formData.get("password") || "");
    const confirmPassword = String(formData.get("confirmPassword") || "");
    if (password !== confirmPassword) {
      setStatus("Passwords do not match.", "error");
      return;
    }
  }

  if (mode === "signup" && signupOtpStep) {
    endpoint = "/auth/verify-signup";
    payload = {
      email: String(formData.get("email") || "").trim(),
      otp: String(formData.get("otp") || "").trim(),
    };
    if (!payload.otp) {
      setStatus("Please enter the OTP from your email.", "error");
      return;
    }
  }

  setStatus(mode === "signup" ? (signupOtpStep ? "Verifying OTP..." : "Creating account...") : "Signing you in...");

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(getErrorMessage(data, mode === "signup" ? "Signup failed." : "Login failed."));
    }

    if (mode === "signup" && !signupOtpStep) {
      signupOtpStep = true;
      if (otpFieldWrap) {
        otpFieldWrap.classList.remove("is-hidden");
      }
      if (otpInput) {
        otpInput.required = true;
        otpInput.focus();
      }
      const actionBtn = form.querySelector(".auth-action");
      if (actionBtn) {
        actionBtn.textContent = "Verify OTP";
      }
      setStatus(data.detail || "OTP sent to your email. Enter it to verify your account.");
      return;
    }

    setStatus("Success. Redirecting...");
    window.location.href = "/";
  } catch (error) {
    setStatus(error.message || "Something went wrong.", "error");
  }
}

if (form) {
  form.addEventListener("submit", handleSubmit);
}

redirectIfLoggedIn();