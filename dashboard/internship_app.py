from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

# Inisialisasi Flask App
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Ganti dengan secret key yang lebih aman

# Fungsi untuk memberikan rekomendasi berdasarkan skills dengan sistem scoring profesional
def get_recommendation(skills_input):
    """
    Memberikan rekomendasi posisi magang berdasarkan skills menggunakan sistem scoring profesional
    Mengembalikan list of dictionary dengan informasi lengkap
    
    Output format:
    [
        {
            "role": "Data Analyst Intern",
            "score": 80,
            "matched_skills": ["python", "sql"],
            "missing_skills": ["tableau", "power bi"],
            "level": "Sangat Cocok",
            "description": "Analisis data dan pembuatan laporan..."
        }
    ]
    """
    
    # Definisi kategori skill dengan keyword yang lengkap
    skill_categories = {
        "data": {
            "skills": ["data", "analysis", "excel", "sql", "tableau", "power bi", "analytics", "database"],
            "role": "Data Analyst Intern",
            "description": "Menganalisis data, membuat laporan, dan memberikan insight bisnis dari data untuk mendukung pengambilan keputusan."
        },
        "programming": {
            "skills": ["python", "javascript", "java", "html", "css", "react", "node", "php", "code", "programming"],
            "role": "Software Developer Intern",
            "description": "Mengembangkan aplikasi dan software, memperbaiki bug, serta berkontribusi dalam siklus pengembangan produk."
        },
        "design": {
            "skills": ["ui", "ux", "figma", "design", "photoshop", "illustrator", "sketch", "adobe"],
            "role": "UI/UX Intern",
            "description": "Mendesain interface pengguna, melakukan user research, dan menciptakan pengalaman pengguna yang optimal."
        },
        "business": {
            "skills": ["management", "leadership", "project", "hr", "business", "strategy", "operations"],
            "role": "Business Development Intern",
            "description": "Mengembangkan strategi bisnis, mencari peluang pasar, dan mendukung pertumbuhan perusahaan."
        },
        "finance": {
            "skills": ["finance", "accounting", "financial", "audit", "tax", "budgeting", "investment"],
            "role": "Finance Intern",
            "description": "Mengelola keuangan, melakukan audit internal, dan menganalisis laporan keuangan perusahaan."
        },
        "marketing": {
            "skills": ["marketing", "seo", "social media", "branding", "content", "advertising", "digital"],
            "role": "Marketing Intern",
            "description": "Membuat strategi pemasaran, mengelola media sosial, dan meningkatkan brand awareness."
        }
    }
    
    # Normalisasi input: lowercase dan hapus spasi berlebih
    skills_list = []
    for skill in skills_input.split(","):
        normalized_skill = skill.strip().lower()
        if normalized_skill:  # Hanya tambahkan jika tidak kosong
            skills_list.append(normalized_skill)
    
    # Debug print (WAJIB)
    print("Skills input:", skills_list)
    
    # Analisis setiap kategori
    recommendations = []
    
    for category, info in skill_categories.items():
        category_skills = info["skills"]
        matched_skills = []
        
        # Cek skill yang cocok
        for skill in skills_list:
            if any(keyword in skill for keyword in category_skills):
                matched_skills.append(skill)
        
        # Jika ada skill yang cocok, buat rekomendasi
        if matched_skills:
            # Hitung persentase kecocokan
            total_category_skills = len(category_skills)
            matched_count = len(matched_skills)
            percentage = int((matched_count / total_category_skills) * 100)
            
            # Tentukan skill yang belum dimiliki
            missing_skills = [skill for skill in category_skills if not any(keyword in user_skill for keyword in [skill] for user_skill in skills_list)]
            
            # Tentukan level kecocokan
            if percentage >= 70:
                level = "Sangat Cocok"
            elif percentage >= 40:
                level = "Cocok"
            else:
                level = "Kurang Cocok"
            
            # Buat dictionary rekomendasi
            recommendation = {
                "role": info["role"],
                "score": percentage,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills[:3],  # Maksimal 3 skill yang disarankan
                "level": level,
                "description": info["description"]
            }
            
            recommendations.append(recommendation)
            print(f"Category '{category}' matched: {matched_skills} -> {percentage}% ({level})")
    
    # Jika tidak ada kategori yang cocok, return general internship
    if not recommendations:
        print("No skills matched, returning General Internship")
        return [{
            "role": "General Internship",
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "level": "Tidak Cocok",
            "description": "Posisi magang umum untuk berbagai departemen dengan tugas yang bervariasi."
        }]
    
    # Urutkan berdasarkan skor tertinggi
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    
    # Tambahkan ranking
    for i, rec in enumerate(recommendations):
        rec["rank"] = i + 1
    
    print("Final recommendations:", [f"#{r['rank']} {r['role']} ({r['score']}%)" for r in recommendations])
    
    # Extract score data for charts
    chart_scores = {}
    category_mapping = {
        "data": "Data",
        "programming": "Programming", 
        "design": "Design",
        "business": "Business",
        "finance": "Finance",
        "marketing": "Marketing"
    }
    
    # Initialize all categories with 0
    for category, display_name in category_mapping.items():
        chart_scores[display_name] = 0
    
    # Update with actual scores from recommendations
    for rec in recommendations:
        for category, display_name in category_mapping.items():
            if display_name in rec["role"]:
                chart_scores[display_name] = rec["score"]
                break
    
    return {
        "recommendations": recommendations,
        "chart_scores": chart_scores
    }


# Route untuk halaman utama (upload)
@app.route('/')
def index():
    return render_template('index.html')

# Route untuk proses form input
@app.route('/process', methods=['POST'])
def process_form():
    # Ambil data dari form
    nama = request.form.get('nama', '').strip()
    skills = request.form.get('skills', '').strip()
    
    # Validasi input
    if not nama:
        flash('Nama harus diisi!')
        return redirect(url_for('index'))
    
    if not skills:
        flash('Skills harus diisi!')
        return redirect(url_for('index'))
    
    # Proses rekomendasi
    result = get_recommendation(skills)
    
    # Simpan hasil ke session
    session['nama'] = nama
    session['skills'] = skills
    session['recommendation'] = result['recommendations']
    session['chart_scores'] = result['chart_scores']
    
    flash('Data berhasil diproses!')
    return redirect(url_for('dashboard'))

# Route untuk dashboard
@app.route('/dashboard')
def dashboard():
    # Periksa apakah ada data rekomendasi
    if 'recommendation' not in session:
        flash('Tidak ada data. Silakan input data terlebih dahulu.')
        return redirect(url_for('index'))
    
    nama = session.get('nama', '')
    skills = session.get('skills', '')
    recommendation = session.get('recommendation', '')
    chart_scores = session.get('chart_scores', {})
    
    return render_template('dashboard.html', 
                         nama=nama,
                         skills=skills,
                         recommendation=recommendation,
                         chart_scores=chart_scores)

# Route API untuk data grafik
@app.route('/api/chart-data')
def chart_data():
    if 'stats' not in session:
        return jsonify({'error': 'No data available'})
    
    stats = session.get('stats', {})
    
    # Format data untuk Chart.js
    chart_data = {
        'labels': list(stats.keys()),
        'data': list(stats.values())
    }
    
    return jsonify(chart_data)

# Route untuk menghapus session data
@app.route('/clear')
def clear_data():
    session.clear()
    flash('Data telah dihapus')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)