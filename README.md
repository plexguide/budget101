# Budget101 - Personal Budget Management System

![Docker Pulls](https://img.shields.io/docker/pulls/admin9705/budget101)
![GitHub release](https://img.shields.io/github/v/release/admin9705/budget101)
![License](https://img.shields.io/github/license/admin9705/budget101)

A comprehensive Flask-based personal budget management application with a dark theme UI inspired by Huntarr. Manage your bills, track taxes, and control your personal finances with ease.

## ✨ Features

- **🏠 Dashboard**: Coming soon - overview of your financial status
- **💳 Bills Management**: Track bills, due dates, and payment status
- **📊 Tax Management**: Organize tax information by year
- **⚙️ Settings**: Customize your experience with user preferences
- **🔐 Authentication**: Secure user registration and login system
- **📱 Responsive Design**: Modern, mobile-friendly interface
- **🐳 Docker Ready**: Easy deployment with Docker

## 🚀 Quick Start

### Docker Deployment (Recommended)

1. **Using Docker Run:**
```bash
docker run -d \
  --name budget101 \
  --restart unless-stopped \
  -p 9715:9715 \
  -v ./config:/config \
  admin9705/budget101:latest
```

2. **Using Docker Compose:**
```yaml
version: '3.8'
services:
  budget101:
    image: admin9705/budget101:latest
    container_name: budget101
    restart: unless-stopped
    ports:
      - "9715:9715"
    volumes:
      - ./config:/config
    environment:
      - TZ=America/New_York
```

3. **Access the application:**
   - Open your browser to `http://localhost:9715`
   - Create your first admin account

## 🔧 Configuration

Budget101 uses a YAML configuration file located at `/config/config.yml`. Copy the example configuration:

```bash
cp config/config.yml.example config/config.yml
```

Key configuration options:
- **Database settings**: SQLite database path and backup options
- **Security settings**: Session timeout, login attempts, etc.
- **Email notifications**: SMTP settings for bill reminders
- **UI preferences**: Currency, timezone, theme options

## 📋 Requirements

- **Python 3.11+** (for development)
- **Docker** (for deployment)
- **Modern web browser**

## 🛠️ Development Setup

1. **Clone the repository:**
```bash
git clone https://github.com/admin9705/budget101.git
cd budget101
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python app.py
```

5. **Access the application:**
   - Open `http://localhost:9715`

## 🏗️ Project Structure

```
budget101/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker build configuration
├── docker-compose.yml    # Docker Compose setup
├── static/               # Static assets (CSS, JS)
│   ├── css/style.css    # Main stylesheet
│   └── js/script.js     # JavaScript functionality
├── templates/            # Jinja2 templates
│   ├── base.html        # Base template
│   ├── auth/            # Authentication pages
│   └── pages/           # Application pages
├── config/              # Configuration files
└── .github/workflows/   # GitHub Actions CI/CD
```

## 🎨 Features Overview

### Bills Management
- Add and track bills with due dates
- Categorize bills (Housing, Utilities, etc.)
- Mark bills as paid/unpaid
- Set recurring bills
- Visual progress tracking

### Tax Management
- Track tax information by year
- Record income, deductions, and payments
- Monitor filing status
- Calculate refunds and amounts owed

### User Settings
- Customize currency and timezone
- Configure notification preferences
- Change passwords securely
- Export data functionality

## 🔒 Security Features

- **Secure Authentication**: bcrypt password hashing
- **Session Management**: Configurable session timeouts
- **Rate Limiting**: Protection against brute force attacks
- **CSRF Protection**: Built-in Flask security
- **Input Validation**: Comprehensive form validation

## 🌐 API Endpoints

Budget101 provides RESTful API endpoints:

- `POST /api/bills` - Add new bills
- `POST /api/taxes` - Add tax records
- `POST /api/settings/user` - Update user settings
- `POST /api/settings/password` - Change password

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](https://github.com/admin9705/budget101/wiki)
- **Issues**: [GitHub Issues](https://github.com/admin9705/budget101/issues)
- **Discussions**: [GitHub Discussions](https://github.com/admin9705/budget101/discussions)

## 🙏 Acknowledgments

- Inspired by [Huntarr.io](https://github.com/plexguide/Huntarr.io) for design and architecture
- Built with [Flask](https://flask.palletsprojects.com/) and [Bootstrap](https://getbootstrap.com/)
- Icons by [Font Awesome](https://fontawesome.com/)

## 📊 Statistics

- **Languages**: Python, HTML, CSS, JavaScript
- **Framework**: Flask
- **Database**: SQLite
- **UI**: Bootstrap 5 with custom dark theme
- **Deployment**: Docker

---

**Made with ❤️ for personal budget management**

![Budget101 Interface](https://via.placeholder.com/800x400/1a1d23/ffffff?text=Budget101+Interface+Preview) 