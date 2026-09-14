# SteelVision

**AI-powered surface defect detection for stainless steel strips** — a YOLOv8 detector behind a FastAPI backend and a Next.js inspection dashboard, built around the NEU-DET surface defect dataset.

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-ff6f00)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## Overview

SteelVision is an AI-assisted visual inspection system for detecting and classifying surface defects on steel-strip images.

The system combines:

- YOLOv8-based defect detection
- FastAPI inference backend
- Next.js inspection dashboard
- Multi-frame inspection workflow
- Bounding-box visualization
- Defect confidence and severity information
- Model performance benchmarking
- Docker-based deployment
- Cloud deployment through Render

The project was built as a portfolio implementation for the **Jindal Stainless Engineering Case Study Competition 2026 — Problem Statement 1**.

---

## Problem

Manual visual inspection of steel strip surfaces can be:

- Slow
- Inconsistent between inspectors
- Difficult to scale
- Dependent on operator attention
- Challenging to integrate with continuous production lines

An automated inspection system should detect defects consistently and present the results in a form that an operator can quickly review.

---

## Solution

SteelVision follows a simple inspection pipeline:

```text
Steel Surface Image
        │
        ▼
Next.js Inspection Dashboard
        │
        ▼
FastAPI /predict
        │
        ▼
InferenceService
        │
        ▼
YOLOv8n Detector
        │
        ▼
Defect Detection
        │
        ├── Defect class
        ├── Confidence
        ├── Bounding box
        ├── Defect count
        ├── Severity score
        └── Inference latency