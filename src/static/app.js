document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and activity select
      activitiesList.innerHTML = "";
      // Remove all options except the first default one
      while (activitySelect.options.length > 1) {
        activitySelect.remove(1);
      }

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <p><strong>📋 Current Participants:</strong></p>
            <ul>
              ${details.participants.map(p => `<li><span class="participant-email clickable" data-activity="${name}" data-email="${p}">${p}</span></li>`).join('')}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);
        
        // Add event listeners to participant names
        activityCard.querySelectorAll('.participant-email.clickable').forEach(participant => {
          participant.addEventListener('click', async (e) => {
            const activity = participant.getAttribute('data-activity');
            const email = participant.getAttribute('data-email');
            
            const confirmed = confirm(`Are you sure you want to remove ${email} from ${activity}?`);
            
            if (confirmed) {
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(activity)}/remove?email=${encodeURIComponent(email)}`,
                  { method: 'DELETE' }
                );
                
                if (response.ok) {
                  messageDiv.textContent = `Removed ${email} from ${activity}`;
                  messageDiv.className = 'success';
                  messageDiv.classList.remove('hidden');
                  fetchActivities();
                  setTimeout(() => messageDiv.classList.add('hidden'), 5000);
                } else {
                  const error = await response.json();
                  messageDiv.textContent = error.detail || 'Failed to remove participant';
                  messageDiv.className = 'error';
                  messageDiv.classList.remove('hidden');
                }
              } catch (error) {
                messageDiv.textContent = 'Error removing participant';
                messageDiv.className = 'error';
                messageDiv.classList.remove('hidden');
                console.error('Error:', error);
              }
            }
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
