function openTab(evt, tabName) {
    // Hide all tab content
    const allTabs = document.querySelectorAll(".tab-content");
    allTabs.forEach(tab => tab.classList.remove("active"));

    // Show the clicked tab's content
    const activeTab = document.getElementById(tabName);
    activeTab.classList.add("active");

  }
