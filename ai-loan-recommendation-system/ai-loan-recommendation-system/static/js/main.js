/**
 * Main JavaScript for LoanAI System.
 * Handles Demo Profile Autofill, Real-time calculations, EMI Calculator, and UI tooltips.
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Auto-compute Annual Income from Monthly Income
    const monthlyIncomeInput = document.getElementById("monthly_income");
    const annualIncomeInput = document.getElementById("annual_income");
    
    if (monthlyIncomeInput && annualIncomeInput) {
        monthlyIncomeInput.addEventListener("input", function () {
            const monthly = parseFloat(this.value) || 0;
            if (!annualIncomeInput.dataset.manualEdit) {
                annualIncomeInput.value = Math.round(monthly * 12);
            }
        });

        annualIncomeInput.addEventListener("input", function() {
            this.dataset.manualEdit = "true";
        });
    }

    // 2. Demo Profile Autofill Buttons
    const demoButtons = document.querySelectorAll("[data-demo-profile]");
    demoButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const profileType = this.getAttribute("data-demo-profile");
            
            // Visual feedback
            const originalHTML = this.innerHTML;
            this.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Loading...`;

            fetch(`/api/demo-profile/${profileType}`)
                .then(res => res.json())
                .then(data => {
                    this.innerHTML = originalHTML;
                    if (data && Object.keys(data).length > 0) {
                        for (const [key, val] of Object.entries(data)) {
                            const field = document.getElementById(key);
                            if (field) {
                                field.value = val;
                                // Trigger change event for select/inputs
                                field.dispatchEvent(new Event("change"));
                                field.dispatchEvent(new Event("input"));
                            }
                        }
                        
                        // Highlight form
                        const formCard = document.getElementById("loanDetectionForm");
                        if (formCard) {
                            formCard.classList.add("border-primary");
                            setTimeout(() => formCard.classList.remove("border-primary"), 1200);
                        }
                    }
                })
                .catch(err => {
                    this.innerHTML = originalHTML;
                    console.error("Failed to load demo profile:", err);
                });
        });
    });

    // 3. Dynamic Interactive EMI Calculator (on Results or standalone page)
    initEmiCalculator();
});

/**
 * Initializes Interactive EMI Calculator with dynamic slider synchronisation
 */
function initEmiCalculator() {
    const amountSlider = document.getElementById("emiAmountSlider");
    const amountInput = document.getElementById("emiAmountInput");
    const tenureSlider = document.getElementById("emiTenureSlider");
    const tenureInput = document.getElementById("emiTenureInput");
    const rateSlider = document.getElementById("emiRateSlider");
    const rateInput = document.getElementById("emiRateInput");

    const emiResultElem = document.getElementById("emiResultValue");
    const totalInterestElem = document.getElementById("emiTotalInterest");
    const totalAmountElem = document.getElementById("emiTotalAmount");

    if (!amountSlider || !amountInput) return;

    function syncAndCalculate(source, target) {
        target.value = source.value;
        calculateEMI();
    }

    amountSlider.addEventListener("input", () => syncAndCalculate(amountSlider, amountInput));
    amountInput.addEventListener("input", () => syncAndCalculate(amountInput, amountSlider));

    tenureSlider.addEventListener("input", () => syncAndCalculate(tenureSlider, tenureInput));
    tenureInput.addEventListener("input", () => syncAndCalculate(tenureInput, tenureSlider));

    rateSlider.addEventListener("input", () => syncAndCalculate(rateSlider, rateInput));
    rateInput.addEventListener("input", () => syncAndCalculate(rateInput, rateSlider));

    function calculateEMI() {
        const P = parseFloat(amountInput.value) || 0;
        const nMonths = parseFloat(tenureInput.value) || 12;
        const annualRate = parseFloat(rateInput.value) || 9.0;

        const r = (annualRate / 12) / 100;
        let emi = 0;
        if (r > 0 && nMonths > 0 && P > 0) {
            emi = (P * r * Math.pow(1 + r, nMonths)) / (Math.pow(1 + r, nMonths) - 1);
        } else if (nMonths > 0) {
            emi = P / nMonths;
        }

        const totalPayable = emi * nMonths;
        const totalInterest = Math.max(0, totalPayable - P);

        if (emiResultElem) emiResultElem.textContent = "₹" + Math.round(emi).toLocaleString("en-IN");
        if (totalInterestElem) totalInterestElem.textContent = "₹" + Math.round(totalInterest).toLocaleString("en-IN");
        if (totalAmountElem) totalAmountElem.textContent = "₹" + Math.round(totalPayable).toLocaleString("en-IN");

        updateEmiChart(P, totalInterest);
    }

    let emiChartInstance = null;
    function updateEmiChart(principal, interest) {
        const ctx = document.getElementById("emiDonutChart");
        if (!ctx) return;

        if (!emiChartInstance) {
            emiChartInstance = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: ["Principal Amount", "Total Interest"],
                    datasets: [{
                        data: [principal, interest],
                        backgroundColor: ["#2563eb", "#f59e0b"],
                        borderWidth: 2,
                        borderColor: "#ffffff"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "bottom" },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.label}: ₹${Math.round(context.raw).toLocaleString("en-IN")}`;
                                }
                            }
                        }
                    },
                    cutout: "70%"
                }
            });
        } else {
            emiChartInstance.data.datasets[0].data = [principal, interest];
            emiChartInstance.update();
        }
    }

    // Initial run
    calculateEMI();
}
