# 🍽️ ChoosyTable

> **Empowering People of Color with corporate interview insights and company transparency data**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)

**Before we lend our talents to any company, we should know how they treat us.**

## 🚀 Quick Start

### Option 1: Mock Authentication (Easiest) ✨
Perfect for development and testing without Google OAuth setup:

```bash
# Clone and setup
git clone <your-repo> && cd choosytable
cp .env.dev .env

# Start services (macOS)
brew install mongodb-community memcached
brew services start mongodb-community memcached

# Run the app
python3 run.py
```

Visit `http://localhost:5000` → Click "Mock Login" → Start testing!

### Option 2: Full OAuth Setup
For production-like testing:

```bash
# Setup environment
cp .env.template .env
# Add your Google OAuth credentials to .env

# Install and run
pip install -r requirements.txt
python3 run.py
```

## 📚 Documentation

Our documentation is organized using a **memory bank structure** for maximum clarity:

### Core Documentation
- **[Project Brief](memory_bank/projectbrief.md)** - Mission, objectives, and technical vision
- **[Product Context](memory_bank/productContext.md)** - Why ChoosyTable exists and how it works
- **[Technical Context](memory_bank/techContext.md)** - Technologies, setup, and constraints
- **[System Patterns](memory_bank/systemPatterns.md)** - Architecture and design patterns
- **[Active Context](memory_bank/activeContext.md)** - Current work focus and recent changes
- **[Progress](memory_bank/progress.md)** - What works, what's left, current status

### Quick Reference
| Need | See |
|------|-----|
| **Local Development** | [Tech Context → Development Setup](memory_bank/techContext.md#development-setup-requirements) |
| **Authentication Setup** | [Tech Context → Environment Configuration](memory_bank/techContext.md#environment-configuration) |
| **Architecture Overview** | [System Patterns](memory_bank/systemPatterns.md) |
| **Performance Info** | [Progress → Performance Metrics](memory_bank/progress.md#performance-metrics-post-optimization) |
| **Recent Changes** | [Active Context](memory_bank/activeContext.md) |

## ⚡ Performance

Recently optimized with dramatic improvements:
- **60-80% faster** database queries
- **50% faster** page loads
- **40% less** memory usage
- **85%** cache hit rate

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask 2.3.3 + Python 3.8+ |
| **Database** | MongoDB 4.0+ |
| **Cache** | Memcached |
| **Auth** | Google OAuth 2.0 (+ Mock for dev) |

## 🤝 Contributing

1. **Read the docs**: Start with [Project Brief](memory_bank/projectbrief.md)
2. **Set up locally**: Use mock auth for fastest setup
3. **Make changes**: Follow patterns in [System Patterns](memory_bank/systemPatterns.md)
4. **Test thoroughly**: Ensure no regressions
5. **Update docs**: Keep memory bank current

## 📞 Support

- **Quick Questions**: Check [memory_bank/](memory_bank/) documentation
- **Issues**: [GitHub Issues](https://github.com/regcam/choosytable/issues)
- **Discussions**: [GitHub Discussions](https://github.com/regcam/choosytable/discussions)

---

**Made with ❤️ for the community**

*Empowering informed career decisions through shared experiences and data-driven insights.*