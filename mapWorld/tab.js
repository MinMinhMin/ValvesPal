function openTab(evt, tabName) {
    const allTabs = document.querySelectorAll(".tab-content");
    allTabs.forEach(tab => tab.classList.remove("active"));

    const activeTab = document.getElementById(tabName);
    activeTab.classList.add("active");

  }
