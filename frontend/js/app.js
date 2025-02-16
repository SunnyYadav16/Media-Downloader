import { currentConfig } from '../config.js';


document.addEventListener('DOMContentLoaded', function () {
  /**
   * Loads an HTML component from a URL into the target element.
   * Once the HTML is injected, an optional callback is invoked.
   */
  async function loadComponent(url, targetSelector, callback) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const html = await response.text();
      const targetElement = document.querySelector(targetSelector);
      if (targetElement) {
        targetElement.innerHTML = html;
        if (callback) {
          callback();
        } // invoke callback after content is loaded
      } else {
        console.error(`Target element '${targetSelector}' not found.`);
      }
    } catch (error) {
      console.error(`Error loading component from ${url}:`, error);
    }
  }

  // Load the main content into #main-container and initialize event listeners when done.
  loadComponent('components/content.html', '#main-container',
    initializeEventListeners);

  // Declare variables that will reference DOM elements once the content is loaded.
  let videoUrlInput, findVideoButton, loadingSpinner, errorMessage,
    resultsContainer, downloadOptions;

  /**
   * Queries for all the necessary elements and attaches event listeners.
   */
  function initializeEventListeners() {
    // Query elements now that the external content has been loaded.
    videoUrlInput = document.querySelector('#video-url');
    findVideoButton = document.querySelector('.find-video-btn');
    loadingSpinner = document.querySelector('.loading-spinner');
    errorMessage = document.querySelector('.error-message');
    resultsContainer = document.querySelector('.results-container');
    downloadOptions = document.querySelector('.download-options');

    // Check that the required elements exist.
    if (!videoUrlInput || !findVideoButton) {
      console.log(
        "Required DOM elements are missing. Ensure '.find-video-btn' and '#video-url' exist.");
      return;
    }

    // Attach event listeners.
    findVideoButton.addEventListener('click', () => {
      const url = videoUrlInput.value.trim();
      if (url) {
        handleSubmit(url);
      } else {
        showError('Please enter a valid YouTube URL');
      }
    });

    videoUrlInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const url = videoUrlInput.value.trim();
        if (url) {
          handleSubmit(url);
        } else {
          showError('Please enter a valid YouTube URL');
        }
      }
    });
  }

  // Utility functions to manage UI state
  function showLoading(show) {
    if (loadingSpinner) {
      loadingSpinner.classList.toggle('hidden', !show);
    }
    if (findVideoButton) {
      findVideoButton.disabled = show;
    }
  }

  function showError(message) {
    if (errorMessage) {
      const p = errorMessage.querySelector('p');
      if (p) {
        p.textContent = message;
      }
      errorMessage.classList.remove('hidden');
    }
  }

  function hideError() {
    if (errorMessage) {
      errorMessage.classList.add('hidden');
    }
  }

  function showResults() {
    if (resultsContainer) {
      resultsContainer.classList.remove('hidden');
    }
  }

  function hideResults() {
    if (resultsContainer) {
      resultsContainer.classList.add('hidden');
    }
  }

  async function handleSubmit(url) {
    try {
      showLoading(true);
      hideError();
      hideResults();

      // Verify URL is valid (you can add your validation logic here)
      if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
        throw new Error('Please enter a valid YouTube URL');
      }

      // Display the initial options (Video/Audio buttons)
      displayInitialOptions(url);
    } catch (error) {
      showError(error.message);
    } finally {
      showLoading(false);
    }
  }

  // New function to display initial Video/Audio options
  function displayInitialOptions(url) {
    const c = document.cookie;
    console.log(c)
    if (downloadOptions) {
      downloadOptions.innerHTML = ''; // Clear previous options

      const container = document.createElement('div');
      container.className = 'download-type-buttons';

      // Create Video Download Button
      const videoBtn = document.createElement('button');
      videoBtn.className = 'download-type-btn';
      videoBtn.textContent = 'Download Video';
      videoBtn.addEventListener('click', () => handleVideoOptions(url));

      // Create Audio Download Button
      const audioBtn = document.createElement('button');
      audioBtn.className = 'download-type-btn';
      audioBtn.textContent = 'Download Audio';
      audioBtn.addEventListener('click', () => handleAudioOptions(url));

      container.appendChild(videoBtn);
      container.appendChild(audioBtn);
      downloadOptions.appendChild(container);
      showResults();
    }
  }

  // Handle video options selection
  async function handleVideoOptions(url) {
    try {
      showLoading(true);
      hideError();

      const response = await fetch(`${currentConfig.apiEndpoint}/formats`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({url: url})
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to process video');
      }

      displayVideoOptions(data, url);
    } catch (error) {
      showError(error.message);
    } finally {
      showLoading(false);
    }
  }

  // Display video format and quality options
  function displayVideoOptions(data, url) {
    if (downloadOptions) {
      downloadOptions.innerHTML = ''; // Clear previous options

      // Create format selection
      const formatSelector = createFormatSelector(data.video_formats);
      downloadOptions.appendChild(formatSelector);

      // Create quality selection
      const qualitySelector = createQualitySelector(data.available_qualities);
      downloadOptions.appendChild(qualitySelector);

      // Add download button
      const downloadButton = createDownloadButton(url);
      downloadOptions.appendChild(downloadButton);

      // Add back button
      const backButton = document.createElement('button');
      backButton.className = 'back-button';
      backButton.textContent = '← Back';
      backButton.addEventListener('click', () => displayInitialOptions(url));
      downloadOptions.appendChild(backButton);
    }
  }

  async function handleVideoDownload(url) {
    const formatSelect = document.querySelector('#format-select');
    const qualitySelect = document.querySelector('#quality-select');
    if (!formatSelect || !qualitySelect) {
      return;
    }

    const format = formatSelect.value;
    const quality = qualitySelect.value;

    try {
      showLoading(true);

      const downloadResponse = await fetch(`${currentConfig.apiEndpoint}/download/video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: url,
          format: format,
          quality: quality
        })
      });

      if (!downloadResponse.ok) {
        throw new Error('Download failed');
      }

      const data = await downloadResponse.json();

      if (data.status === 'success' && data.message) {
        // Clear the previous options
        downloadOptions.innerHTML = '';

        // Create download link button
        const downloadLinkBtn = document.createElement('button');
        downloadLinkBtn.className = 'download-link-button';
        downloadLinkBtn.textContent = 'Download Link';
        downloadLinkBtn.addEventListener('click', () => {
          const link = document.createElement('a');
          link.href = data.message;
          link.download = ''; // This will preserve the original filename
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        });

        // Create container for the download link button
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'download-link-container';
        buttonContainer.appendChild(downloadLinkBtn);

        // Add back button
        const backButton = document.createElement('button');
        backButton.className = 'back-button';
        backButton.textContent = '← Back';
        backButton.addEventListener('click', () => displayInitialOptions(url));
        buttonContainer.appendChild(backButton);

        downloadOptions.appendChild(buttonContainer);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      showError('Download failed: ' + error.message);
    } finally {
      showLoading(false);
    }
  }

// Add handleAudioOptions function (implement, according to your audio download requirements)
  async function handleAudioOptions(url) {
    try {
      showLoading(true);
      hideError();

      const response = await fetch(`${currentConfig.apiEndpoint}/formats`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({url: url})
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to process audio');
      }

      displayAudioOptions(data, url);
    } catch (error) {
      showError(error.message);
    } finally {
      showLoading(false);
    }
  }

  // Display audio format and quality options
  function displayAudioOptions(data, url) {
    if (downloadOptions) {
      downloadOptions.innerHTML = ''; // Clear previous options

      // Create format selection
      const formatSelector = createAudioFormatSelector(data.audio_formats);
      downloadOptions.appendChild(formatSelector);

      // Create quality selection
      const qualitySelector = createAudioQualitySelector(data.available_qualities);
      downloadOptions.appendChild(qualitySelector);

      // Add download button
      const downloadButton = createAudioDownloadButton(url);
      downloadOptions.appendChild(downloadButton);

      // Add back button
      const backButton = document.createElement('button');
      backButton.className = 'back-button';
      backButton.textContent = '← Back';
      backButton.addEventListener('click', () => displayInitialOptions(url));
      downloadOptions.appendChild(backButton);
    }
  }

  function createAudioFormatSelector(formats) {
    const container = document.createElement('div');
    container.className = 'format-selector download-option';

    const label = document.createElement('label');
    label.textContent = 'Select Audio Format:';

    const select = document.createElement('select');
    select.id = 'audio-format-select';
    formats.forEach(format => {
      const option = document.createElement('option');
      option.value = format;
      option.textContent = format.toUpperCase();
      select.appendChild(option);
    });

    container.appendChild(label);
    container.appendChild(select);
    return container;
  }

  function createAudioQualitySelector(qualities) {
    const container = document.createElement('div');
    container.className = 'quality-selector download-option';

    const label = document.createElement('label');
    label.textContent = 'Select Audio Quality:';

    const select = document.createElement('select');
    select.id = 'audio-quality-select';
    Object.keys(qualities).forEach(quality => {
      const option = document.createElement('option');
      option.value = quality;
      option.textContent = quality;
      select.appendChild(option);
    });

    container.appendChild(label);
    container.appendChild(select);
    return container;
  }

  function createAudioDownloadButton(url) {
    const container = document.createElement('div');
    container.className = 'download-button-container';

    const button = document.createElement('button');
    button.className = 'download-button';
    button.textContent = 'Download';
    button.addEventListener('click', () => handleAudioDownload(url));

    container.appendChild(button);
    return container;
  }

  async function handleAudioDownload(url) {
    const formatSelect = document.querySelector('#audio-format-select');
    const qualitySelect = document.querySelector('#audio-quality-select');
    if (!formatSelect || !qualitySelect) {
      return;
    }

    const format = formatSelect.value;
    const quality = qualitySelect.value;

    try {
      showLoading(true);

      const downloadResponse = await fetch(`${currentConfig.apiEndpoint}/download/audio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: url,
          format: format,
          quality: quality
        })
      });

      if (!downloadResponse.ok) {
        throw new Error('Download failed');
      }

      const data = await downloadResponse.json();

      if (data.status === 'success' && data.message) {
        // Clear the previous options
        downloadOptions.innerHTML = '';

        // Create download link button
        const downloadLinkBtn = document.createElement('button');
        downloadLinkBtn.className = 'download-link-button';
        downloadLinkBtn.textContent = 'Download Link';
        downloadLinkBtn.addEventListener('click', () => {
          const link = document.createElement('a');
          link.href = data.message;
          link.download = ''; // This will preserve the original filename
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        });

        // Create container for the download link button
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'download-link-container';
        buttonContainer.appendChild(downloadLinkBtn);

        // Add back button
        const backButton = document.createElement('button');
        backButton.className = 'back-button';
        backButton.textContent = '← Back';
        backButton.addEventListener('click', () => displayInitialOptions(url));
        buttonContainer.appendChild(backButton);

        downloadOptions.appendChild(buttonContainer);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      showError('Download failed: ' + error.message);
    } finally {
      showLoading(false);
    }
  }

  function createFormatSelector(formats) {
    const container = document.createElement('div');
    container.className = 'format-selector download-option';

    const label = document.createElement('label');
    label.textContent = 'Select Video Format:';

    const select = document.createElement('select');
    select.id = 'format-select';
    formats.forEach(format => {
      const option = document.createElement('option');
      option.value = format;
      option.textContent = format.toUpperCase();
      select.appendChild(option);
    });

    container.appendChild(label);
    container.appendChild(select);
    return container;
  }

  function createQualitySelector(qualities) {
    const container = document.createElement('div');
    container.className = 'quality-selector download-option';

    const label = document.createElement('label');
    label.textContent = 'Select Video Quality:';

    const select = document.createElement('select');
    select.id = 'quality-select';
    Object.keys(qualities).forEach(quality => {
      const option = document.createElement('option');
      option.value = quality;
      option.textContent = quality;
      select.appendChild(option);
    });

    container.appendChild(label);
    container.appendChild(select);
    return container;
  }

  // Modify createDownloadButton to pass the URL
  function createDownloadButton(url) {
    const container = document.createElement('div');
    container.className = 'download-button-container';

    const button = document.createElement('button');
    button.className = 'download-button';
    button.textContent = 'Download';
    button.addEventListener('click', () => handleVideoDownload(url));

    container.appendChild(button);
    return container;
  }
});
