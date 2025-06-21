const login = () => {
  const form = document.getElementById("loginForm");
  const alert = document.getElementById("errorAlert");

  form.addEventListener("submit", e => {
    e.preventDefault();
    const user = document.getElementById("username").value.trim();
    const pass = document.getElementById("password").value.trim();

    if (user === "admin" && pass === "pinface2") {
      localStorage.setItem("isAdminLoggedIn", "true");
      window.location = "admin.html";
    } else {
      alert.classList.remove("d-none");
    }
  });
};

window.addEventListener("load", login);
