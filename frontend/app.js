// Lead Intelligence Dashboard
class LeadsDashboard {
    constructor() {
        this.leads = [];
        this.filteredLeads = [];
        this.currentPage = 1;
        this.pageSize = 10;
        this.currentFilter = "all";
        this.searchQuery = "";

        this.initElements();
        this.bindEvents();
        this.loadLeads();
    }

    initElements() {
        this.searchInput = document.getElementById("search-input");
        this.filterButtons = document.querySelectorAll(".btn-filter");
        this.leadsTbody = document.getElementById("leads-tbody");
        this.prevBtn = document.getElementById("prev-btn");
        this.nextBtn = document.getElementById("next-btn");
        this.pageInfo = document.getElementById("page-info");
        this.exportBtn = document.getElementById("export-btn");
        this.refreshBtn = document.getElementById("refresh-btn");
    }

    bindEvents() {
        this.searchInput.addEventListener("input", (e) => this.handleSearch(e));
        this.filterButtons.forEach((btn) => {
            btn.addEventListener("click", (e) => this.handleFilter(e));
        });
        this.prevBtn.addEventListener("click", () => this.prevPage());
        this.nextBtn.addEventListener("click", () => this.nextPage());
        this.exportBtn.addEventListener("click", () => this.exportCSV());
        this.refreshBtn.addEventListener("click", () => this.loadLeads());
    }

    async loadLeads() {
        try {
            // Try to load from API first, fallback to static data
            const response = await fetch("/api/leads", { headers: { "Accept": "application/json" } }).catch(() => null);
            if (response && response.ok) {
                this.leads = await response.json();
            } else {
                // Use sample data if no API available
                this.leads = this.getSampleLeads();
            }
            this.applyFilters();
            this.updateStats();
            this.render();
        } catch (err) {
            console.error("Failed to load leads:", err);
            this.leads = this.getSampleLeads();
            this.applyFilters();
            this.updateStats();
            this.render();
        }
    }

    getSampleLeads() {
        return [
            {
                id: "1",
                company: { name: "Northwind Traders" },
                website: "https://northwind.example",
                contact_name: "Robert King",
                contact_title: "CEO & Founder",
                contact_email: "robert.king@northwind.example",
                contact_phone: "+1 (555) 123-4567",
                email: "info@northwind.example",
                phone: "+1 (555) 123-4567",
                status: "qualified",
                confidence_score: 0.92,
                source: "opencorporates",
            },
            {
                id: "2",
                company: { name: "Contoso Corporation" },
                website: "https://contoso.example",
                contact_name: "Emily Peterson",
                contact_title: "Founder & President",
                contact_email: "emily.peterson@contoso.example",
                contact_phone: "+1 (555) 234-5678",
                email: "sales@contoso.example",
                phone: "+1 (555) 234-5678",
                status: "new",
                confidence_score: 0.85,
                source: "business_directory",
            },
            {
                id: "3",
                company: { name: "Fabrikam Inc" },
                website: "https://fabrikam.example",
                contact_name: "Marcus Johnson",
                contact_title: "Owner & Executive Director",
                contact_email: "marcus.johnson@fabrikam.example",
                contact_phone: "+1 (555) 345-6789",
                email: "contact@fabrikam.example",
                phone: "+1 (555) 345-6789",
                status: "contacted",
                confidence_score: 0.78,
                source: "website",
            },
        ];
    }

    handleSearch(e) {
        this.searchQuery = e.target.value.toLowerCase();
        this.currentPage = 1;
        this.applyFilters();
        this.render();
    }

    handleFilter(e) {
        this.filterButtons.forEach((btn) => btn.classList.remove("active"));
        e.target.classList.add("active");
        this.currentFilter = e.target.dataset.filter;
        this.currentPage = 1;
        this.applyFilters();
        this.render();
    }

    applyFilters() {
        this.filteredLeads = this.leads.filter((lead) => {
            const matchesFilter =
                this.currentFilter === "all" || lead.status === this.currentFilter;
            const matchesSearch =
                !this.searchQuery ||
                lead.company.name.toLowerCase().includes(this.searchQuery) ||
                (lead.email && lead.email.toLowerCase().includes(this.searchQuery)) ||
                (lead.contact_email && lead.contact_email.toLowerCase().includes(this.searchQuery)) ||
                (lead.contact_name && lead.contact_name.toLowerCase().includes(this.searchQuery)) ||
                (lead.website && lead.website.toLowerCase().includes(this.searchQuery));
            return matchesFilter && matchesSearch;
        });
    }

    updateStats() {
        const totalLeads = this.leads.length;
        const qualifiedLeads = this.leads.filter((l) => l.status === "qualified").length;
        const pendingLeads = this.leads.filter((l) =>
            ["new", "contacted"].includes(l.status)
        ).length;
        const conversionRate =
            totalLeads > 0 ? Math.round((qualifiedLeads / totalLeads) * 100) : 0;

        document.getElementById("total-leads").textContent = totalLeads;
        document.getElementById("qualified-leads").textContent = qualifiedLeads;
        document.getElementById("pending-leads").textContent = pendingLeads;
        document.getElementById("conversion-rate").textContent = `${conversionRate}%`;
    }

    render() {
        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const paginatedLeads = this.filteredLeads.slice(start, end);

        if (paginatedLeads.length === 0) {
            this.leadsTbody.innerHTML =
                '<tr><td colspan="7" class="empty-state">No leads found.</td></tr>';
        } else {
            this.leadsTbody.innerHTML = paginatedLeads
                .map((lead) => this.renderRow(lead))
                .join("");
        }

        this.updatePagination();
    }

    renderRow(lead) {
        const companyName = lead.company?.name || "N/A";
        const website = lead.website || "N/A";
        const contactName = lead.contact_name || "N/A";
        const contactTitle = lead.contact_title || "N/A";
        const contactEmail = lead.contact_email || "N/A";
        const contactPhone = lead.contact_phone || "N/A";
        const statusBadgeClass = `status-${lead.status || "new"}`;
        const statusText = (lead.status || "new").toUpperCase();
        const score = (lead.confidence_score * 100).toFixed(0);

        return `
            <tr>
                <td>${this.escape(companyName)}</td>
                <td><a href="${this.escape(website)}" target="_blank">${this.escape(website)}</a></td>
                <td><strong>${this.escape(contactName)}</strong><br><small>${this.escape(contactTitle)}</small></td>
                <td><a href="mailto:${this.escape(contactEmail)}">${this.escape(contactEmail)}</a></td>
                <td><a href="tel:${this.escape(contactPhone)}">${this.escape(contactPhone)}</a></td>
                <td><span class="status-badge ${statusBadgeClass}">${statusText}</span></td>
                <td>${score}%</td>
                <td><button class="btn btn-secondary" onclick="alert('Feature coming soon')">View</button></td>
            </tr>
        `;
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredLeads.length / this.pageSize);
        this.pageInfo.textContent = `Page ${this.currentPage} of ${Math.max(totalPages, 1)}`;
        this.prevBtn.disabled = this.currentPage === 1;
        this.nextBtn.disabled = this.currentPage >= totalPages;
    }

    prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.render();
            window.scrollTo({ top: 0, behavior: "smooth" });
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.filteredLeads.length / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.render();
            window.scrollTo({ top: 0, behavior: "smooth" });
        }
    }

    exportCSV() {
        const headers = ["Company", "Website", "Contact Name", "Contact Title", "Contact Email", "Contact Phone", "Status", "Score"];
        const rows = this.filteredLeads.map((lead) => [
            lead.company?.name || "",
            lead.website || "",
            lead.contact_name || "",
            lead.contact_title || "",
            lead.contact_email || "",
            lead.contact_phone || "",
            lead.status || "",
            (lead.confidence_score * 100).toFixed(0),
        ]);

        let csv = headers.join(",") + "\n";
        rows.forEach((row) => {
            csv += row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",") + "\n";
        });

        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);

        link.setAttribute("href", url);
        link.setAttribute("download", `leads_${new Date().toISOString().split("T")[0]}.csv`);
        link.style.visibility = "hidden";

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    escape(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    new LeadsDashboard();
});
