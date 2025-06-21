const BASE_URL = "http://127.0.0.1:8000";

const adminInit = () => {
  if (localStorage.getItem("isAdminLoggedIn") !== "true") {
    window.location = "login.html";
    return;
  }

  document.getElementById("dashboard-tab").addEventListener("click", e => {
    e.preventDefault();
    cargarDashboard();
  });

  document.getElementById("access-logs-tab").addEventListener("click", e => {
    e.preventDefault();
    cargarLogs();
  });

  document.getElementById("users-tab").addEventListener("click", e => {
    e.preventDefault();
    cargarUsuarios();
  });

  document.getElementById("logout-btn").addEventListener("click", e => {
    e.preventDefault();
    cerrarSesion();
  });

  document.addEventListener("click", e => {
    if (e.target.classList.contains("ver-detalles")) {
      const userId = e.target.dataset.id;
      mostrarDetalles(userId);
    }
  });

  cargarDashboard();
};

const cargarDashboard = () => {
  showLoading();
  fetch(`${BASE_URL}/dashboard-data`)
    .then(res => {
      if (!res.ok) throw new Error(`Error HTTP! estado: ${res.status}`);
      return res.json();
    })
    .then(data => {
      document.getElementById("total-users").textContent = data.total_usuarios || "0";
      document.getElementById("today-access").textContent = data.accesos_hoy || "0";
      document.getElementById("last-access").textContent = data.ultimo_acceso || "Ninguno";

      document.getElementById("dashboard-cards").classList.remove("d-none");
      document.getElementById("logs-container").classList.add("d-none");
      document.getElementById("users-content").classList.add("d-none");

      setActiveTab("dashboard-tab");
    })
    .catch(err => {
      console.error("Error al cargar dashboard:", err);
      alert("Error al cargar datos del dashboard");
    })
    .finally(hideLoading);
};

const cargarLogs = () => {
  showLoading();
  fetch(`${BASE_URL}/logs`)
    .then(res => {
      if (!res.ok) throw new Error(`Error HTTP! estado: ${res.status}`);
      return res.json();
    })
    .then(data => {
      const tbody = document.querySelector("#logsTable tbody");
      tbody.innerHTML = "";

      data.forEach(log => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${log.id}</td>
          <td>${log.username}</td>
          <td>${new Date(log.access_time).toLocaleString()}</td>
        `;
        tbody.appendChild(row);
      });

      document.getElementById("dashboard-cards").classList.add("d-none");
      document.getElementById("logs-container").classList.remove("d-none");
      document.getElementById("users-content").classList.add("d-none");

      setActiveTab("access-logs-tab");
    })
    .catch(err => {
      console.error("Error al cargar logs:", err);
      alert("Error al cargar registros de acceso");
    })
    .finally(hideLoading);
};

const cargarUsuarios = () => {
  showLoading();
  fetch(`${BASE_URL}/usuarios`)
    .then(res => {
      if (!res.ok) throw new Error(`Error HTTP! estado: ${res.status}`);
      return res.json();
    })
    .then(data => {
      const tbody = document.querySelector("#users-table tbody");
      tbody.innerHTML = "";

      data.forEach(user => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${user.id}</td>
          <td>${user.nombre}</td>
          <td>${user.username}</td>
          <td><button class="btn btn-sm btn-primary ver-detalles" data-id="${user.id}">Ver</button></td>
        `;
        tbody.appendChild(row);
      });

      if ($.fn.DataTable.isDataTable("#users-table")) {
        $("#users-table").DataTable().destroy();
      }
      $("#users-table").DataTable();

      document.getElementById("dashboard-cards").classList.add("d-none");
      document.getElementById("logs-container").classList.add("d-none");
      document.getElementById("users-content").classList.remove("d-none");

      setActiveTab("users-tab");
    })
    .catch(err => {
      console.error("Error al cargar usuarios:", err);
      alert("Error al cargar lista de usuarios");
    })
    .finally(hideLoading);
};

const mostrarDetalles = userId => {
  showLoading();
  fetch(`${BASE_URL}/usuarios/${userId}`)
    .then(res => {
      if (!res.ok) throw new Error(`Error HTTP! estado: ${res.status}`);
      return res.json();
    })
    .then(user => {
      document.getElementById("modal-user-name").textContent = user.nombre || "N/A";
      document.getElementById("modal-user-username").textContent = user.username || "N/A";
      document.getElementById("modal-user-lastaccess").textContent = user.ultimo_acceso || "Nunca";
      document.getElementById("modal-user-totalaccess").textContent = user.total_accesos || "0";

      new bootstrap.Modal(document.getElementById("userModal")).show();
    })
    .catch(err => {
      console.error("Error al cargar detalles:", err);
      alert("Error al cargar detalles del usuario");
    })
    .finally(hideLoading);
};

const cerrarSesion = () => {
  showLoading();
  fetch(`${BASE_URL}/auth/logout`, {
    method: "POST",
    credentials: "include"
  })
    .then(res => {
      if (!res.ok) throw new Error(`Error HTTP! estado: ${res.status}`);
      localStorage.removeItem("isAdminLoggedIn");
      window.location = "login.html";
    })
    .catch(err => {
      console.error("Error al cerrar sesión:", err);
      localStorage.removeItem("isAdminLoggedIn");
      window.location = "login.html";
    });
};

const setActiveTab = tabId => {
  document.querySelectorAll(".nav-link").forEach(link => link.classList.remove("active"));
  document.getElementById(tabId).classList.add("active");
};

const showLoading = () => {
};

const hideLoading = () => {
};

window.addEventListener("load", adminInit);
