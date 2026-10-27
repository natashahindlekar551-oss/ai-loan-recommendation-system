/**
 * Online Document Submission & Live Camera Scanner Module
 * Provides camera streaming via HTML5 getUserMedia, snapshot capturing,
 * shutter audio feedback, direct file upload, and document previewing/retaking.
 */

class DocumentManager {
    constructor() {
        this.currentAppId = null;
        this.currentDocName = null;
        this.currentDocCategory = null;
        this.stream = null;
        this.facingMode = "environment"; // default back camera on phones, fallback on webcams
        this.capturedBase64 = null;
        
        this.initDOMElements();
        this.bindEvents();
    }

    initDOMElements() {
        // Modals
        this.cameraModalEl = document.getElementById("cameraScanModal");
        this.cameraModal = this.cameraModalEl ? new bootstrap.Modal(this.cameraModalEl) : null;

        this.uploadModalEl = document.getElementById("fileUploadModal");
        this.uploadModal = this.uploadModalEl ? new bootstrap.Modal(this.uploadModalEl) : null;

        this.previewModalEl = document.getElementById("docPreviewModal");
        this.previewModal = this.previewModalEl ? new bootstrap.Modal(this.previewModalEl) : null;

        // Camera Elements
        this.video = document.getElementById("cameraVideo");
        this.canvas = document.getElementById("cameraCanvas");
        this.snapshotPreview = document.getElementById("snapshotPreview");
        this.shutterBtn = document.getElementById("shutterBtn");
        this.retakeBtn = document.getElementById("retakeBtn");
        this.confirmScanBtn = document.getElementById("confirmScanBtn");
        this.switchCamBtn = document.getElementById("switchCameraBtn");
        this.cameraFlash = document.getElementById("cameraFlash");
        this.cameraDocTitle = document.getElementById("cameraDocTitle");

        // Upload Form Elements
        this.uploadDocTitle = document.getElementById("uploadDocTitle");
        this.fileInput = document.getElementById("docFileInput");
        this.uploadSubmitBtn = document.getElementById("uploadSubmitBtn");

        // Preview Elements
        this.previewDocTitle = document.getElementById("previewDocTitle");
        this.previewContainer = document.getElementById("previewContainer");
    }

    bindEvents() {
        // Open Camera Scan Modal
        document.querySelectorAll("[data-action='scan-camera']").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const appId = btn.getAttribute("data-app-id");
                const docName = btn.getAttribute("data-doc-name");
                const docCategory = btn.getAttribute("data-doc-category");
                this.openCameraModal(appId, docName, docCategory);
            });
        });

        // Open File Upload Modal
        document.querySelectorAll("[data-action='upload-file']").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const appId = btn.getAttribute("data-app-id");
                const docName = btn.getAttribute("data-doc-name");
                const docCategory = btn.getAttribute("data-doc-category");
                this.openUploadModal(appId, docName, docCategory);
            });
        });

        // Open Document Preview
        document.querySelectorAll("[data-action='preview-doc']").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const docId = btn.getAttribute("data-doc-id");
                const docName = btn.getAttribute("data-doc-name");
                this.openPreviewModal(docId, docName);
            });
        });

        // Delete / Retake Document
        document.querySelectorAll("[data-action='delete-doc']").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const docId = btn.getAttribute("data-doc-id");
                const docName = btn.getAttribute("data-doc-name");
                if (confirm(`Do you want to remove '${docName}' to re-scan or re-upload?`)) {
                    this.deleteDocument(docId, docName);
                }
            });
        });

        // Shutter Button Click
        if (this.shutterBtn) {
            this.shutterBtn.addEventListener("click", () => this.takeSnapshot());
        }

        // Retake Snapshot Button
        if (this.retakeBtn) {
            this.retakeBtn.addEventListener("click", () => this.retakeSnapshot());
        }

        // Confirm & Submit Camera Scan
        if (this.confirmScanBtn) {
            this.confirmScanBtn.addEventListener("click", () => this.submitCameraScan());
        }

        // Switch Camera Facing (User / Environment)
        if (this.switchCamBtn) {
            this.switchCamBtn.addEventListener("click", () => this.toggleCameraFacing());
        }

        // Standard File Upload Submit
        if (this.uploadSubmitBtn) {
            this.uploadSubmitBtn.addEventListener("click", (e) => {
                e.preventDefault();
                this.submitFileUpload();
            });
        }

        // Clean up video stream on modal close
        if (this.cameraModalEl) {
            this.cameraModalEl.addEventListener("hidden.bs.modal", () => {
                this.stopCameraStream();
            });
        }
    }

    async openCameraModal(appId, docName, docCategory) {
        this.currentAppId = appId;
        this.currentDocName = docName;
        this.currentDocCategory = docCategory;

        if (this.cameraDocTitle) {
            this.cameraDocTitle.textContent = `Scanning: ${docName}`;
        }

        // Reset display
        this.capturedBase64 = null;
        if (this.video) this.video.style.display = "block";
        if (this.snapshotPreview) this.snapshotPreview.style.display = "none";
        if (this.shutterBtn) this.shutterBtn.style.display = "flex";
        if (this.retakeBtn) this.retakeBtn.style.display = "none";
        if (this.confirmScanBtn) this.confirmScanBtn.style.display = "none";

        if (this.cameraModal) this.cameraModal.show();
        await this.startCameraStream();
    }

    async startCameraStream() {
        this.stopCameraStream();
        try {
            const constraints = {
                video: {
                    facingMode: this.facingMode,
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                },
                audio: false
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            if (this.video) {
                this.video.srcObject = this.stream;
                await this.video.play();
            }
        } catch (err) {
            console.error("Camera access error:", err);
            // Fallback: try default without facingMode
            try {
                this.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
                if (this.video) {
                    this.video.srcObject = this.stream;
                    await this.video.play();
                }
            } catch (fallbackErr) {
                alert("Camera permission denied or camera unavailable. Please grant permission or use the 'Upload Document' option.");
                if (this.cameraModal) this.cameraModal.hide();
            }
        }
    }

    stopCameraStream() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        if (this.video) {
            this.video.srcObject = null;
        }
    }

    async toggleCameraFacing() {
        this.facingMode = this.facingMode === "environment" ? "user" : "environment";
        await this.startCameraStream();
    }

    playShutterSound() {
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(800, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(300, audioCtx.currentTime + 0.08);
            gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.09);
        } catch (e) {
            // Audio context not allowed or not supported
        }
    }

    takeSnapshot() {
        if (!this.video || !this.canvas) return;

        // Visual flash & Audio click
        this.playShutterSound();
        if (this.cameraFlash) {
            this.cameraFlash.classList.add("flash-active");
            setTimeout(() => this.cameraFlash.classList.remove("flash-active"), 250);
        }

        // Draw video frame to canvas
        const width = this.video.videoWidth || 1280;
        const height = this.video.videoHeight || 720;
        this.canvas.width = width;
        this.canvas.height = height;

        const ctx = this.canvas.getContext("2d");
        ctx.drawImage(this.video, 0, 0, width, height);

        // Convert to Base64 JPEG
        this.capturedBase64 = this.canvas.toDataURL("image/jpeg", 0.92);

        // Show captured image preview
        if (this.snapshotPreview) {
            this.snapshotPreview.src = this.capturedBase64;
            this.snapshotPreview.style.display = "block";
        }
        if (this.video) this.video.style.display = "none";

        // Toggle buttons
        if (this.shutterBtn) this.shutterBtn.style.display = "none";
        if (this.retakeBtn) this.retakeBtn.style.display = "inline-flex";
        if (this.confirmScanBtn) this.confirmScanBtn.style.display = "inline-flex";

        // Pause stream temporarily
        this.stopCameraStream();
    }

    async retakeSnapshot() {
        this.capturedBase64 = null;
        if (this.snapshotPreview) this.snapshotPreview.style.display = "none";
        if (this.video) this.video.style.display = "block";

        if (this.shutterBtn) this.shutterBtn.style.display = "flex";
        if (this.retakeBtn) this.retakeBtn.style.display = "none";
        if (this.confirmScanBtn) this.confirmScanBtn.style.display = "none";

        await this.startCameraStream();
    }

    submitCameraScan() {
        if (!this.capturedBase64) return;

        const submitBtn = this.confirmScanBtn;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin me-1"></i> Uploading...`;
        submitBtn.disabled = true;

        const formData = new FormData();
        formData.append("doc_name", this.currentDocName);
        formData.append("doc_category", this.currentDocCategory);
        formData.append("is_camera_scan", "true");
        formData.append("camera_image_base64", this.capturedBase64);

        fetch(`/api/documents/upload/${this.currentAppId}`, {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            if (data.success) {
                if (this.cameraModal) this.cameraModal.hide();
                // Reload page to display fresh verification status and preview button
                window.location.reload();
            } else {
                alert("Upload failed: " + (data.error || "Unknown error"));
            }
        })
        .catch(err => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            console.error("Upload error:", err);
            alert("Error submitting document scan. Please try again.");
        });
    }

    openUploadModal(appId, docName, docCategory) {
        this.currentAppId = appId;
        this.currentDocName = docName;
        this.currentDocCategory = docCategory;

        if (this.uploadDocTitle) {
            this.uploadDocTitle.textContent = `Upload: ${docName}`;
        }
        if (this.fileInput) this.fileInput.value = "";
        if (this.uploadModal) this.uploadModal.show();
    }

    submitFileUpload() {
        if (!this.fileInput || !this.fileInput.files || this.fileInput.files.length === 0) {
            alert("Please choose a file to upload.");
            return;
        }

        const file = this.fileInput.files[0];
        const submitBtn = this.uploadSubmitBtn;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin me-1"></i> Submitting...`;
        submitBtn.disabled = true;

        const formData = new FormData();
        formData.append("doc_name", this.currentDocName);
        formData.append("doc_category", this.currentDocCategory);
        formData.append("is_camera_scan", "false");
        formData.append("file", file);

        fetch(`/api/documents/upload/${this.currentAppId}`, {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            if (data.success) {
                if (this.uploadModal) this.uploadModal.hide();
                window.location.reload();
            } else {
                alert("Upload failed: " + (data.error || "Unknown error"));
            }
        })
        .catch(err => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            console.error("Upload error:", err);
            alert("Error uploading document. Please try again.");
        });
    }

    openPreviewModal(docId, docName) {
        if (this.previewDocTitle) {
            this.previewDocTitle.textContent = `Document Preview: ${docName}`;
        }

        const previewUrl = `/api/documents/preview/${docId}`;
        if (this.previewContainer) {
            this.previewContainer.innerHTML = `
                <div class="text-center p-3">
                    <img src="${previewUrl}" class="img-fluid rounded shadow-sm border" style="max-height: 520px; object-fit: contain;" alt="${docName}" onerror="this.onerror=null; this.parentElement.innerHTML='<iframe src=\\'${previewUrl}\\' style=\\'width:100%; height:500px; border:none;\\'></iframe>';">
                </div>
            `;
        }

        if (this.previewModal) this.previewModal.show();
    }

    deleteDocument(docId, docName) {
        fetch(`/api/documents/delete/${docId}`, {
            method: "POST"
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                alert("Failed to remove document: " + (data.error || "Unknown error"));
            }
        })
        .catch(err => {
            console.error("Delete error:", err);
            alert("Error removing document.");
        });
    }
}

// Instantiate on page load
document.addEventListener("DOMContentLoaded", () => {
    window.docManager = new DocumentManager();
});
