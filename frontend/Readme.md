# Media Downloader Frontend

A lightweight web interface for downloading media content from various online platforms using pure HTML, CSS, and JavaScript.

---

## 🌟 Features
- Browser-based media URL submission
- Simple UI with form validation
- Responsive design for all devices
- Progress indicators for download status
- Platform compatibility without build tools

---

## Dir Structure
```
frontend/
├── components/
│     ├── content.html    # Main content section
├── css/
│     ├── style.css       # Main stylesheet
├── images/
│     ├── favicon.ico     # Favicon for tab
│     └── icon.png        # App icon (png format)
│     └── icon.svg        # App icon (svg format)
├── js/
│     ├── app.js          # Main JavaScript file
│     └── config.jpg      # Configuration file
│
├── index.html            # Main HTML file
├── 404.html              # Error page
└── README.md             # Project documentation
```

---

## Quick Start
1. Download or clone the repository:
```bash
git clone https://github.com/SunnyYadav16/Media-Downloader.git
```
2. Navigate to the frontend folder:
```bash
cd Media-Downloader/frontend
```
3. Open `index.html` in your browser:
  - Right-click the file > "Open with" > Choose Chrome/Firefox/Safari
  - Or drag the file directly into an open browser window

4. Configuration:
   - Set your API endpoint in `js/config.js`:
```javascript
const API_ENDPOINT = 'https://your-api-server.com/app/v1/youtube';
```

---

## Technologies Used
- HTML5 Semantic Elements
- CSS3 (Flexbox/Grid)
- Vanilla JavaScript (ES6+)
- Fetch API for backend communication

---

## Browser Support
- Google Chrome 60+
- Firefox 55+
- Safari 11+
- Microsoft Edge 17+

---

## Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Test changes directly in browser
4. Submit a Pull Request

---

## License
[MIT](https://github.com/SunnyYadav16/Media-Downloader/blob/main/LICENSE.txt)

