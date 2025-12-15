// Simple Profile Page JS

function openEditModal() {
    document.getElementById('edit-modal').classList.add('active');
}

function closeEditModal() {
    document.getElementById('edit-modal').classList.remove('active');
}

async function saveProfile() {
    const firstName = document.getElementById('first-name').value.trim();
    const lastName = document.getElementById('last-name').value.trim();
    const email = document.getElementById('email').value.trim();

    if (!firstName || !email) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        const response = await fetch('/api/profile/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                email: email
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Update UI
            document.getElementById('display-name').textContent = `${firstName} ${lastName}`;
            document.getElementById('display-email').textContent = email;

            const avatar = document.querySelector('.avatar');
            if (avatar) {
                avatar.textContent = firstName.charAt(0).toUpperCase() + (lastName ? lastName.charAt(0).toUpperCase() : '');
            }

            closeEditModal();

            setTimeout(() => window.location.reload(), 500);
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Failed to update profile');
    }
}

// Close on background click
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('edit-modal');
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeEditModal();
            }
        });
    }
});
