function showError(message) {
    const errorDiv = document.getElementById("error-message");
    errorDiv.textContent = message;
    errorDiv.style.display = "block";
    setTimeout(() => {
        errorDiv.style.display = "none";
    }, 5000);
}

function validateAddForm(tableName) {
    let isValid = true;
    let errorMessage = "";

    if (tableName === "Users") {
        const phone = document.getElementById("phone").value;
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const phonePattern = /^[0-9]{11}$/;
        if (!phonePattern.test(phone)) {
            errorMessage = "Phone must be exactly 11 digits (e.g., 12345678901)";
            isValid = false;
        }
        if (!username) {
            errorMessage = "Username is required";
            isValid = false;
        }
        if (!password) {
            errorMessage = "Password is required";
            isValid = false;
        }
    } else if (tableName === "Friends") {
        const status = document.getElementById("status").value;
        if (!["0", "1"].includes(status)) {
            errorMessage = "Status must be 0 or 1";
            isValid = false;
        }
    } else if (tableName === "Group_Members") {
        const role = document.getElementById("role").value;
        if (!["0", "1", "2"].includes(role)) {
            errorMessage = "Role must be 0, 1, or 2";
            isValid = false;
        }
    } else if (tableName === "Messages") {
        const messageType = document.getElementById("message_type").value;
        const receiverId = document.getElementById("receiver_id").value;
        const groupId = document.getElementById("group_id").value;
        const content = document.getElementById("content").value;

        if (!["0", "1", "2"].includes(messageType)) {
            errorMessage = "Message Type must be 0, 1, or 2";
            isValid = false;
        }
        if (!receiverId && !groupId) {
            errorMessage = "Either Receiver ID or Group ID must be provided";
            isValid = false;
        }
        if (!content) {
            errorMessage = "Content is required";
            isValid = false;
        }
    } else if (tableName === "Message_Attachments") {
        const fileType = document.getElementById("file_type").value;
        const fileUrl = document.getElementById("file_url").value;

        if (fileType && !["image", "file"].includes(fileType)) {
            errorMessage = "File Type must be 'image', 'file', or empty";
            isValid = false;
        }
        if (!fileUrl) {
            errorMessage = "File URL is required";
            isValid = false;
        }
    }

    if (!isValid) {
        showError(errorMessage);
    }
    return isValid;
}

function validateEditForm(tableName, recordId) {
    let isValid = true;
    let errorMessage = "";

    if (tableName === "Users") {
        const phone = document.getElementById(`phone_${recordId}`).value;
        const username = document.getElementById(`username_${recordId}`).value;
        const password = document.getElementById(`password_${recordId}`).value;

        const phonePattern = /^[0-9]{11}$/;
        if (!phonePattern.test(phone)) {
            errorMessage = "Phone must be exactly 11 digits (e.g., 12345678901)";
            isValid = false;
        }
        if (!username) {
            errorMessage = "Username is required";
            isValid = false;
        }
        if (!password) {
            errorMessage = "Password is required";
            isValid = false;
        }
    } else if (tableName === "Friends") {
        const status = document.getElementById(`status_${recordId}`).value;
        if (!["0", "1"].includes(status)) {
            errorMessage = "Status must be 0 or 1";
            isValid = false;
        }
    } else if (tableName === "Group_Members") {
        const role = document.getElementById(`role_${recordId}`).value;
        if (!["0", "1", "2"].includes(role)) {
            errorMessage = "Role must be 0, 1, or 2";
            isValid = false;
        }
    } else if (tableName === "Messages") {
        const messageType = document.getElementById(`message_type_${recordId}`).value;
        const receiverId = document.getElementById(`receiver_id_${recordId}`).value;
        const groupId = document.getElementById(`group_id_${recordId}`).value;
        const content = document.getElementById(`content_${recordId}`).value;

        if (!["0", "1", "2"].includes(messageType)) {
            errorMessage = "Message Type must be 0, 1, or 2";
            isValid = false;
        }
        if (!receiverId && !groupId) {
            errorMessage = "Either Receiver ID or Group ID must be provided";
            isValid = false;
        }
        if (!content) {
            errorMessage = "Content is required";
            isValid = false;
        }
    } else if (tableName === "Message_Attachments") {
        const fileType = document.getElementById(`file_type_${recordId}`).value;
        const fileUrl = document.getElementById(`file_url_${recordId}`).value;

        if (fileType && !["image", "file"].includes(fileType)) {
            errorMessage = "File Type must be 'image', 'file', or empty";
            isValid = false;
        }
        if (!fileUrl) {
            errorMessage = "File URL is required";
            isValid = false;
        }
    }

    if (!isValid) {
        showError(errorMessage);
    }
    return isValid;
}

function editRow(id) {
    const editRow = document.getElementById(`edit_${id}`);
    editRow.style.display = "table-row";
    const dataRow = editRow.previousElementSibling;
    dataRow.style.display = "none";
}

function cancelEdit(id) {
    const editRow = document.getElementById(`edit_${id}`);
    editRow.style.display = "none";
    const dataRow = editRow.previousElementSibling;
    dataRow.style.display = "table-row";
}