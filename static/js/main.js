// Global toast function
function showToast(message, type = 'info') {
    const toast = document.getElementById('liveToast');
    const toastBody = document.getElementById('toastMessage');
    toastBody.textContent = message;
    
    if (type === 'error') {
        toastBody.style.color = '#ef4444'; // Red error
    } else {
        toastBody.style.color = 'var(--text-color)';
    }

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Theme management and drag & drop setup
document.addEventListener('DOMContentLoaded', () => {
    
    // --- Theme Toggle Logic ---
    const themeToggleBtn = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'dark';
    
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            let theme = document.documentElement.getAttribute('data-theme');
            let newTheme = theme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        if (theme === 'dark') {
            themeToggleBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
            themeToggleBtn.className = 'btn btn-sm btn-outline-info rounded-circle d-flex align-items-center justify-content-center';
        } else {
            themeToggleBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
            themeToggleBtn.className = 'btn btn-sm btn-outline-dark rounded-circle d-flex align-items-center justify-content-center';
        }
    }

    // --- Drag & Drop Setup ---
    const dropZone = document.getElementById('dropZone');
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const pwdInput = document.getElementById('passwordInput');
    const pwdStrength = document.getElementById('pwdStrength');
    const msgInput = document.getElementById('messageInput');
    const msgLength = document.getElementById('msgLength');
    
    if (dropZone && imageInput) {
        dropZone.addEventListener('click', () => imageInput.click());
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                imageInput.files = e.dataTransfer.files;
                handleImageSelect(e.dataTransfer.files[0]);
            }
        });
        
        imageInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                handleImageSelect(e.target.files[0]);
            }
        });
    }

    if (pwdInput && pwdStrength) {
        pwdInput.addEventListener('input', (e) => {
            const val = e.target.value;
            pwdStrength.className = 'pwd-strength';
            if (val.length === 0) return;
            if (val.length < 6) pwdStrength.classList.add('pwd-weak');
            else if (val.length < 10) pwdStrength.classList.add('pwd-medium');
            else pwdStrength.classList.add('pwd-strong');
        });
    }

    if (msgInput && msgLength) {
        msgInput.addEventListener('input', (e) => {
            const len = e.target.value.length;
            msgLength.textContent = len;
            updateCapacity(len);
        });
    }

    function handleImageSelect(file) {
        if (!file.type.match('image.*')) {
            showToast('Please select a valid image file.', 'error');
            return;
        }
        
        window.currentAnalysisFile = file; // Store for report generation

        const reader = new FileReader();
        reader.onload = (e) => {
            if (imagePreview) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                dropZone.querySelector('i').style.display = 'none';
                dropZone.querySelector('p').textContent = file.name;
                
                // Approximate capacity for encoding
                if (document.getElementById('capacityInfo')) {
                    const img = new Image();
                    img.onload = function() {
                        // Max bytes = (W * H * 3) / 8
                        const maxBytes = Math.floor((this.width * this.height * 3) / 8);
                        window.maxImageCapacity = maxBytes;
                        document.getElementById('capacityInfo').classList.remove('d-none');
                        document.getElementById('maxCapacity').textContent = maxBytes.toLocaleString();
                        updateCapacity(document.getElementById('messageInput').value.length);
                    };
                    img.src = e.target.result;
                }
            }
        };
        reader.readAsDataURL(file);
    }
});

function updateCapacity(msgLen) {
    if (!window.maxImageCapacity) return;
    const max = window.maxImageCapacity;
    // rough estimate: text utf-8 encoding + aes overhead (approx 48 bytes + padding) + magic headers (8 bytes)
    const estimatedUsage = msgLen * 2 + 100;
    const rem = max - estimatedUsage;
    
    document.getElementById('remCapacity').textContent = Math.max(0, rem).toLocaleString();
    
    const pct = Math.min(100, Math.max(0, (estimatedUsage / max) * 100));
    const bar = document.getElementById('capacityBar');
    bar.style.width = pct + '%';
    
    if (pct > 90) bar.style.backgroundColor = '#ef4444';
    else bar.style.backgroundColor = 'var(--neon-blue)';
}

async function handleEncode(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    if (!formData.get('image').name) {
        showToast('Please select an image first.', 'error');
        return;
    }

    toggleLoader(true);
    
    try {
        const response = await fetch('/encode', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'encoded_image.png';
            document.body.appendChild(a);
            a.click();
            a.remove();
            
            showToast('Message encrypted and hidden successfully!');
            form.reset();
            document.getElementById('imagePreview').style.display = 'none';
            document.getElementById('capacityInfo').classList.add('d-none');
            document.getElementById('dropZone').querySelector('i').style.display = 'block';
            document.getElementById('dropZone').querySelector('p').textContent = 'Drag & Drop or Click to Browse';
            document.getElementById('pwdStrength').className = 'pwd-strength';
            document.getElementById('msgLength').textContent = '0';
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to encode image', 'error');
        }
    } catch (err) {
        showToast('An error occurred during encoding.', 'error');
    }
    
    toggleLoader(false);
}

async function handleDecode(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    if (!formData.get('image').name) {
        showToast('Please select an image first.', 'error');
        return;
    }

    toggleLoader(true);
    document.getElementById('resultBox').classList.add('d-none');
    
    try {
        const response = await fetch('/decode', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Message successfully extracted and decrypted!');
            document.getElementById('resultText').textContent = data.message;
            document.getElementById('resultBox').classList.remove('d-none');
        } else {
            showToast(data.error || 'Failed to decode image. Check password or image.', 'error');
        }
    } catch (err) {
        showToast('An error occurred during decoding.', 'error');
    }
    
    toggleLoader(false);
}

async function handleAnalysis(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    if (!formData.get('image').name) {
        showToast('Please select an image first.', 'error');
        return;
    }

    toggleLoader(true);
    document.getElementById('analysisResults').classList.add('d-none');
    
    try {
        const response = await fetch('/analysis', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('Analysis complete!');
            populateAnalysisTable(data.data);
            document.getElementById('analysisResults').classList.remove('d-none');
        } else {
            showToast(data.error || 'Failed to analyze image.', 'error');
        }
    } catch (err) {
        showToast('An error occurred during analysis.', 'error');
    }
    
    toggleLoader(false);
}

document.addEventListener('DOMContentLoaded', () => {
    const reportBtn = document.getElementById('downloadReportBtn');
    if (reportBtn) {
        reportBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (!window.currentAnalysisFile) {
                showToast('No image selected for report.', 'error');
                return;
            }
            
            const originalText = reportBtn.innerHTML;
            reportBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';
            reportBtn.disabled = true;
            
            const fd = new FormData();
            fd.append('image', window.currentAnalysisFile);
            
            try {
                const response = await fetch('/report', { method: 'POST', body: fd });
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'StegShield_Report.pdf';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    showToast('Report downloaded successfully!');
                } else {
                    const data = await response.json();
                    showToast(data.error || 'Failed to generate report', 'error');
                }
            } catch(err) {
                showToast('An error occurred.', 'error');
            }
            
            reportBtn.innerHTML = originalText;
            reportBtn.disabled = false;
        });
    }
});

function populateAnalysisTable(data) {
    const props = ['resolution', 'file_size', 'color_mode', 'channels', 'estimated_capacity'];
    const stego = ['hidden_data_detected', 'encoding', 'encrypted', 'header', 'confidence'];
    
    let propsHtml = '';
    props.forEach(p => {
        if (data[p] !== undefined) {
            const label = p.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            propsHtml += `<tr><th scope="row" class="text-white-50">${label}</th><td class="text-white">${data[p]}</td></tr>`;
        }
    });
    document.getElementById('propertiesTable').innerHTML = propsHtml;

    let stegoHtml = '';
    stego.forEach(p => {
        if (data[p] !== undefined) {
            const label = p.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            let val = data[p];
            if (val === 'Yes' || val === 'Found') {
                val = `<span class="text-neon-green fw-bold">${val}</span>`;
            } else if (val === 'No' || val === 'Not Found') {
                val = `<span class="text-white-50">${val}</span>`;
            }
            stegoHtml += `<tr><th scope="row" class="text-white-50">${label}</th><td class="text-white">${val}</td></tr>`;
        }
    });
    document.getElementById('stegoTable').innerHTML = stegoHtml;
}

function toggleLoader(show) {
    document.getElementById('loader').style.display = show ? 'flex' : 'none';
    document.getElementById('submitBtn').disabled = show;
}
