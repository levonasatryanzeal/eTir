const form = document.getElementById("register-form");
const projectSelect = document.getElementById("project_id");
const errorBox = document.getElementById("form-error");
const submitButton = document.getElementById("submit-button");
const successPanel = document.getElementById("success-panel");
const successEmail = document.getElementById("success-email");

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function clearError() {
  errorBox.textContent = "";
  errorBox.hidden = true;
}

function formatError(body) {
  if (Array.isArray(body.detail)) {
    return body.detail.map((item) => item.msg).join("; ");
  }
  return body.detail || "Не удалось создать аккаунт. Попробуйте ещё раз.";
}

async function loadProjects() {
  try {
    const response = await fetch("/api/projects");
    if (!response.ok) {
      throw new Error("failed");
    }
    const projects = await response.json();

    projectSelect.innerHTML = "";
    if (projects.length === 0) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "Нет доступных проектов";
      projectSelect.append(option);
      projectSelect.disabled = true;
      submitButton.disabled = true;
      showError("Нет доступных проектов для регистрации.");
      return;
    }

    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Выберите проект";
    projectSelect.append(placeholder);

    for (const project of projects) {
      const option = document.createElement("option");
      option.value = String(project.project_id);
      option.textContent = project.project_name;
      projectSelect.append(option);
    }
  } catch {
    projectSelect.innerHTML = "<option value=\"\">Не удалось загрузить</option>";
    projectSelect.disabled = true;
    submitButton.disabled = true;
    showError("Не удалось загрузить список проектов.");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();

  const data = new FormData(form);
  if (data.get("password") !== data.get("confirm_password")) {
    showError("Пароли не совпадают.");
    return;
  }

  const payload = {
    fname: data.get("fname"),
    lname: data.get("lname"),
    email: data.get("email"),
    password: data.get("password"),
    project_id: Number(data.get("project_id")),
  };

  submitButton.disabled = true;
  submitButton.textContent = "Создаём…";

  try {
    const response = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json().catch(() => ({}));

    if (!response.ok) {
      showError(formatError(body));
      return;
    }

    form.closest(".card").hidden = true;
    successEmail.textContent = body.email;
    successPanel.hidden = false;
  } catch {
    showError("Сеть недоступна. Проверьте подключение и попробуйте снова.");
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Создать аккаунт";
  }
});

loadProjects();
