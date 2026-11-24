
document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // 1. MOBILE SIDEBAR
    // =====================================

    const sidebar = document.getElementById("sidebar");
    const menuToggle = document.getElementById("menuToggle");
    const menuOverlay = document.getElementById("menuOverlay");

    function closeSidebar() {
        sidebar?.classList.remove("open");
        menuOverlay?.classList.remove("show");
    }

    menuToggle?.addEventListener("click", () => {
        sidebar?.classList.toggle("open");
        menuOverlay?.classList.toggle("show");
    });

    menuOverlay?.addEventListener("click", closeSidebar);


    // =====================================
    // 2. SIDEBAR NAVIGATION
    // =====================================

    const navLinks = document.querySelectorAll(
        ".sidebar-nav a[data-section]"
    );

    const sections = document.querySelectorAll(".section");
    const pageTitle = document.getElementById("pageTitle");

    navLinks.forEach(link => {

        link.addEventListener("click", event => {
            event.preventDefault();

            const sectionId = link.dataset.section;

            sections.forEach(section => {
                section.classList.remove("active");
            });

            navLinks.forEach(nav => {
                nav.classList.remove("active");
            });

            document.getElementById(sectionId)?.classList.add("active");

            link.classList.add("active");

            pageTitle.textContent = link.textContent.trim();

            closeSidebar();
        });

    });


    // =====================================
    // 3. API REQUEST HELPER
    // =====================================

    async function apiRequest(url, data = null) {

        const options = {
            method: data ? "POST" : "GET",
            headers: {
                "Content-Type": "application/json"
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);

        let result;

        try {
            result = await response.json();
        } catch {
            throw new Error("Invalid server response");
        }

        if (!response.ok || result.success === false) {
            throw new Error(
                result.message || "Something went wrong"
            );
        }

        return result.data ?? result;
    }


    // =====================================
    // 4. SYSTEM MONITORING
    // =====================================

    async function updateSystemStats() {

        try {

            const result = await apiRequest("/api/system");

            const cpu = result.cpu_percent ?? result.cpu_usage;
            const memory = result.memory_percent ?? result.memory_usage;
            const disk = result.disk_percent ?? result.disk_usage;
            const cores = result.cpu_cores ?? result.logical_cores;

            setText("cpuUsage", formatPercent(cpu));
            setText("memoryUsage", formatPercent(memory));
            setText("diskUsage", formatPercent(disk));
            setText("cpuCores", cores ?? "--");

            setText("platform", result.platform ?? "--");
            setText("processor", result.processor || "System CPU");
            setText("systemStatus", "System is running");

        } catch (error) {

            setText("systemStatus", "Monitoring unavailable");
            console.error("System monitoring:", error.message);

        }

    }

    function formatPercent(value) {
        if (value === undefined || value === null) return "--%";
        return Number(value).toFixed(1) + "%";
    }

    function setText(id, value) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }

    updateSystemStats();
    setInterval(updateSystemStats, 3000);


    // =====================================
    // 5. RESULT DISPLAY
    // =====================================

    function showResult(id, data) {

        const box = document.getElementById(id);

        if (!box) return;

        const pre = document.createElement("pre");

        pre.textContent = JSON.stringify(data, null, 2);

        box.replaceChildren(pre);

    }

    function showError(id, error) {

        const box = document.getElementById(id);

        if (!box) return;

        const message = document.createElement("p");

        message.style.color = "#ff8499";
        message.textContent = "Error: " + error.message;

        box.replaceChildren(message);

    }


    // =====================================
    // 6. INPUT HELPERS
    // =====================================

    function parseNumbers(value) {

        const numbers = value
            .split(",")
            .map(item => Number(item.trim()));

        if (
            numbers.length === 0 ||
            numbers.some(number =>
                !Number.isFinite(number) || number < 0
            )
        ) {
            throw new Error("Enter valid comma-separated numbers.");
        }

        return numbers;

    }

    function parseMatrix(value) {

        const rows = value
            .trim()
            .split(/\n|;/)
            .filter(row => row.trim() !== "")
            .map(row => parseNumbers(row));

        if (rows.length === 0) {
            throw new Error("Enter a valid matrix.");
        }

        const columns = rows[0].length;

        if (rows.some(row => row.length !== columns)) {
            throw new Error("Every matrix row must have equal columns.");
        }

        return rows;

    }


    // =====================================
    // 7. CPU SCHEDULING
    // =====================================

    const cpuForm = document.getElementById("cpuForm");

    cpuForm?.addEventListener("submit", async event => {

        event.preventDefault();

        const button = cpuForm.querySelector("button");

        try {

            button.disabled = true;
            button.textContent = "Processing...";

            const data = {

                algorithm: document.getElementById("cpuAlgorithm").value,

                arrival_times: parseNumbers(
                    document.getElementById("arrivalTimes").value
                ),

                burst_times: parseNumbers(
                    document.getElementById("burstTimes").value
                ),

                priorities: document.getElementById("priorities").value.trim()
                    ? parseNumbers(document.getElementById("priorities").value)
                    : [],

                time_quantum: Number(
                    document.getElementById("timeQuantum").value
                )

            };

            if (data.arrival_times.length !== data.burst_times.length) {
                throw new Error("Arrival and burst times must have equal length.");
            }

            if (data.priorities.length &&
                data.priorities.length !== data.burst_times.length) {
                throw new Error("Priority count must match process count.");
            }

            const result = await apiRequest("/api/cpu", data);

            showResult("cpuResult", result);

        } catch (error) {

            showError("cpuResult", error);

        } finally {

            button.disabled = false;
            button.textContent = "Run CPU Scheduling";

        }

    });


    // =====================================
    // 8. MEMORY MANAGEMENT
    // =====================================

    const memoryForm = document.getElementById("memoryForm");

    memoryForm?.addEventListener("submit", async event => {

        event.preventDefault();

        const button = memoryForm.querySelector("button");

        try {

            button.disabled = true;
            button.textContent = "Processing...";

            const data = {

                algorithm: document.getElementById("memoryAlgorithm").value,

                blocks: parseNumbers(
                    document.getElementById("memoryBlocks").value
                ),

                processes: parseNumbers(
                    document.getElementById("processSizes").value
                )

            };

            const result = await apiRequest("/api/memory", data);

            showResult("memoryResult", result);

        } catch (error) {

            showError("memoryResult", error);

        } finally {

            button.disabled = false;
            button.textContent = "Run Memory Allocation";

        }

    });


    // =====================================
    // 9. BANKER'S ALGORITHM
    // =====================================

    const deadlockForm = document.getElementById("deadlockForm");

    deadlockForm?.addEventListener("submit", async event => {

        event.preventDefault();

        const button = deadlockForm.querySelector("button");

        try {

            button.disabled = true;
            button.textContent = "Analyzing...";

            const data = {

                allocation: parseMatrix(
                    document.getElementById("allocationMatrix").value
                ),

                max: parseMatrix(
                    document.getElementById("maxMatrix").value
                ),

                available: parseNumbers(
                    document.getElementById("availableResources").value
                )

            };

            const result = await apiRequest("/api/deadlock", data);

            showResult("deadlockResult", result);

        } catch (error) {

            showError("deadlockResult", error);

        } finally {

            button.disabled = false;
            button.textContent = "Check System Safety";

        }

    });


    // =====================================
    // 10. DISK SCHEDULING
    // =====================================

    const diskForm = document.getElementById("diskForm");

    diskForm?.addEventListener("submit", async event => {

        event.preventDefault();

        const button = diskForm.querySelector("button");

        try {

            button.disabled = true;
            button.textContent = "Processing...";

            const data = {

                algorithm: document.getElementById("diskAlgorithm").value,

                requests: parseNumbers(
                    document.getElementById("requestQueue").value
                ),

                head: Number(
                    document.getElementById("headPosition").value
                ),

                disk_size: Number(
                    document.getElementById("diskSize").value
                ),

                direction: document.getElementById("diskDirection").value

            };

            if (!Number.isInteger(data.head) ||
                !Number.isInteger(data.disk_size) ||
                data.disk_size <= 0) {
                throw new Error("Enter valid head position and disk size.");
            }

            const result = await apiRequest("/api/disk", data);

            showResult("diskResult", result);

        } catch (error) {

            showError("diskResult", error);

        } finally {

            button.disabled = false;
            button.textContent = "Run Disk Scheduling";

        }

    });


    console.log("OS Nexus JavaScript loaded successfully.");

});
