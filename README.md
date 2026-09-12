# Scamlex

Scamlex is a scam detection and online safety platform designed to help users identify potentially fraudulent messages, links, and other suspicious content.

The project analyzes text and URLs for common scam indicators such as urgent requests, suspicious links, requests for sensitive information, money requests, fake rewards, threats, and other deceptive patterns.

## What the Project Does

Scamlex provides users with tools to:

* Scan messages and text for possible scam indicators.
* Check suspicious links and URLs.
* Identify common scam patterns and tactics.
* Generate a risk score based on detected indicators.
* Explain why content was flagged as suspicious.
* Keep track of previous scans.
* Access scam protection directly while browsing through a Chrome extension.

## Main Components

### Web Application

A modern web interface where users can scan content, view results, and manage their scan history.

### Backend

A Python-based backend responsible for the core scam detection system, API endpoints, URL analysis, and database operations.

### Chrome Extension

The Scamlex Guard browser extension provides real-time protection while browsing by analyzing suspicious content on webpages.

### Database

A SQLite database is used to store scam detection patterns and application data.

## Technology Stack

* **Frontend:** React, TypeScript, Vite
* **Backend:** Python, FastAPI
* **Database:** SQLite
* **Browser Extension:** JavaScript, HTML, CSS
* **Authentication:** Supabase
* **Testing:** Playwright

## Purpose

The main goal of Scamlex is to make it easier for people to recognize online scams before they interact with suspicious messages, links, or websites.

> **Stay aware. Stay protected. Check before you trust.**
