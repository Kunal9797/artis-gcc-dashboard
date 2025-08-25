#!/usr/bin/env python3
"""
GCC Intelligence Dashboard - Multi-tab comprehensive analysis
Focus on buyer intelligence with accurate data from mirror imports
"""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import sqlite3
import json
from datetime import datetime
import pandas as pd
import numpy as np

app = FastAPI(title="GCC Intelligence Dashboard")

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass  # Static directory might not exist

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('data/processed/gcc_mirror_intelligence.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the multi-tab dashboard"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Artis Laminates - GCC Market Intelligence</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .header {
            background: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        /* Compact Filter Bar */
        .filter-bar {
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
            transition: all 0.3s ease;
        }
        
        .filter-bar-inner {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px;
            overflow-x: auto;
        }
        
        .filter-bar-inner::-webkit-scrollbar {
            height: 4px;
        }
        
        .filter-bar-inner::-webkit-scrollbar-thumb {
            background: #ddd;
            border-radius: 2px;
        }
        
        .filter-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            background: #f0f4ff;
            border: 1px solid #d4e0ff;
            border-radius: 20px;
            cursor: pointer;
            white-space: nowrap;
            font-size: 14px;
            font-weight: 500;
            color: #333;
            transition: all 0.2s ease;
            position: relative;
        }
        
        .filter-chip:hover {
            background: #e8efff;
            border-color: #667eea;
            transform: translateY(-1px);
        }
        
        .filter-chip.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .filter-chip .icon {
            font-size: 16px;
        }
        
        .filter-chip .value {
            color: #667eea;
            font-weight: 600;
        }
        
        .filter-chip.active .value {
            color: white;
        }
        
        .filter-chip .arrow {
            font-size: 10px;
            opacity: 0.6;
        }
        
        /* Filter Dropdown Panel */
        .filter-dropdown {
            display: none;
            position: absolute;
            top: calc(100% + 8px);
            left: 20px;
            right: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            z-index: 1000;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease, opacity 0.3s ease;
            opacity: 0;
        }
        
        .filter-dropdown.active {
            display: block;
            max-height: 500px;
            opacity: 1;
        }
        
        .filter-dropdown-inner {
            padding: 20px;
            max-height: 450px;
            overflow-y: auto;
        }
        
        .filter-dropdown-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .filter-dropdown-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
        .filter-dropdown-close {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #f5f5f5;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }
        
        .filter-dropdown-close:hover {
            background: #e0e0e0;
        }
        
        .filter-dropdown-content {
            display: grid;
            gap: 12px;
        }
        
        .filter-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.3);
            z-index: 99;
        }
        
        .filter-overlay.active {
            display: block;
        }
        
        /* Apply Button in Bar */
        .filter-apply-btn {
            padding: 8px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-left: auto;
        }
        
        .filter-apply-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102,126,234,0.3);
        }
        
        /* Compact Checkbox List */
        .compact-checkbox-list {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }
        
        .compact-checkbox-item {
            display: flex;
            align-items: center;
            padding: 6px;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s ease;
        }
        
        .compact-checkbox-item:hover {
            background: #f5f7ff;
        }
        
        .compact-checkbox-item input {
            width: 18px;
            height: 18px;
            margin-right: 8px;
            cursor: pointer;
            accent-color: #667eea;
        }
        
        .compact-checkbox-item label {
            cursor: pointer;
            font-size: 14px;
            user-select: none;
        }
        
        /* Compact Select */
        .compact-select {
            width: 100%;
            padding: 10px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            cursor: pointer;
        }
        
        .compact-select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        /* Compact Input */
        .compact-input {
            width: 100%;
            padding: 10px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .compact-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .tabs {
            display: flex;
            background: white;
            margin: 0 20px;
            border-radius: 10px 10px 0 0;
            overflow: hidden;
        }
        
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            background: #f8f9fa;
            border: none;
            font-size: 14px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
        }
        
        .tab.active {
            background: white;
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }
        
        .tab:hover {
            background: #e9ecef;
        }
        
        .content {
            background: white;
            margin: 0 20px 20px;
            padding: 20px;
            border-radius: 0 0 10px 10px;
            min-height: 500px;
        }
        
        .tab-content {
            display: none;
            overflow-x: auto;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .stat-label {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .table-container {
            overflow-x: auto;
            margin: 20px 0;
            max-width: 100%;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: auto;
        }
        
        th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #dee2e6;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        td:hover {
            white-space: normal;
            word-wrap: break-word;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            position: relative;
            height: 400px;
        }
        
        .chart-container canvas {
            max-height: 350px !important;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .filter-bar-inner {
                padding: 10px;
            }
            
            .filter-chip {
                font-size: 13px;
                padding: 6px 12px;
            }
            
            .compact-checkbox-list {
                grid-template-columns: 1fr;
            }
            
            .filter-dropdown {
                left: 10px;
                right: 10px;
            }
        }
        
        .buyer-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        
        .buyer-name {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .buyer-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            font-size: 14px;
        }
        
        .buyer-stat {
            display: flex;
            flex-direction: column;
        }
        
        .buyer-stat-label {
            color: #666;
            font-size: 12px;
        }
        
        .buyer-stat-value {
            font-weight: 600;
            color: #333;
        }
        
        .highlight {
            background: #fff3cd;
            padding: 2px 5px;
            border-radius: 3px;
        }
        
        .single-side-buyer {
            border-left-color: #28a745;
        }
        
        .double-side-buyer {
            border-left-color: #dc3545;
        }
        
        .mixed-buyer {
            border-left-color: #ffc107;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="header" style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); padding: 25px; border-bottom: 3px solid #FFD700;">
        <div style="display: flex; align-items: center; justify-content: space-between; max-width: 1400px; margin: 0 auto;">
            <div style="display: flex; align-items: center; gap: 25px;">
                <!-- Actual Artis Logo -->
                <div style="background: white; padding: 5px; border-radius: 8px;">
                    <img src="/static/artis_logo.png" 
                         alt="Artis Logo" 
                         style="width: 60px; height: auto; object-fit: contain; filter: none;" />
                </div>
                <div>
                    <h1 style="color: #2c3e50; font-size: 32px; font-weight: 700; margin: 0; font-family: 'Segoe UI', Tahoma, sans-serif;">ARTIS LAMINATES</h1>
                    <h2 style="color: #7f8c8d; font-size: 16px; font-weight: 400; margin: 5px 0;">GCC Market Intelligence Platform</h2>
                </div>
            </div>
            <div style="text-align: right;">
                <p style="color: #95a5a6; font-size: 12px; margin: 0;">Data Period: Jan 2023 - Jul 2025</p>
                <p style="color: #27ae60; font-size: 14px; font-weight: 600; margin: 5px 0;">23,575 Import Records</p>
                <p style="color: #3498db; font-size: 12px; margin: 0;">Last Updated: Aug 2025</p>
            </div>
        </div>
    </div>
    
    <!-- Compact Filter Bar -->
    <div class="filter-bar">
        <div class="filter-bar-inner">
            <div class="filter-chip" onclick="toggleFilterDropdown('countries')" id="countriesChip">
                <span class="icon">🌍</span>
                <span class="label">Countries:</span>
                <span class="value" id="countriesValue">All</span>
                <span class="arrow">▼</span>
            </div>
            
            <div class="filter-chip" onclick="toggleFilterDropdown('product')" id="productChip">
                <span class="icon">📦</span>
                <span class="label">Type:</span>
                <span class="value" id="productValue">All</span>
                <span class="arrow">▼</span>
            </div>
            
            <div class="filter-chip" onclick="toggleFilterDropdown('size')" id="sizeChip">
                <span class="icon">📐</span>
                <span class="label">Size:</span>
                <span class="value" id="sizeValue">All</span>
                <span class="arrow">▼</span>
            </div>
            
            <div class="filter-chip" onclick="toggleFilterDropdown('thickness')" id="thicknessChip">
                <span class="icon">📏</span>
                <span class="label">Thickness:</span>
                <span class="value" id="thicknessValue">All</span>
                <span class="arrow">▼</span>
            </div>
            
            <div class="filter-chip" onclick="toggleFilterDropdown('value')" id="valueChip">
                <span class="icon">💰</span>
                <span class="label">Min Value:</span>
                <span class="value" id="valueValue">$0</span>
                <span class="arrow">▼</span>
            </div>
            
            <div class="filter-chip" onclick="toggleFilterDropdown('date')" id="dateChip">
                <span class="icon">📅</span>
                <span class="label">Date:</span>
                <span class="value" id="dateValue">All Time</span>
                <span class="arrow">▼</span>
            </div>
            
            <button class="filter-apply-btn" onclick="applyFilters()">
                Apply Filters
            </button>
            <button class="filter-apply-btn" style="background: #27ae60; margin-left: 10px;" onclick="exportToExcel()">
                📊 Export to Excel
            </button>
        </div>
        
        <!-- Filter Dropdowns -->
        <div class="filter-dropdown" id="countriesDropdown">
            <div class="filter-dropdown-inner">
                <div class="filter-dropdown-header">
                    <div class="filter-dropdown-title">Select Countries</div>
                    <button class="filter-dropdown-close" onclick="closeFilterDropdown('countries')">✕</button>
                </div>
                <div class="filter-dropdown-content">
                    <div style="margin-bottom: 12px;">
                        <label style="display: flex; align-items: center; font-weight: 600;">
                            <input type="checkbox" id="selectAll" checked style="margin-right: 8px;">
                            Select All Countries
                        </label>
                    </div>
                    <div class="compact-checkbox-list" id="countryCheckboxes">
                        <div class="compact-checkbox-item">
                            <input type="checkbox" value="SAUDI ARABIA" checked id="country_sa">
                            <label for="country_sa">🇸🇦 Saudi Arabia</label>
                        </div>
                        <div class="compact-checkbox-item">
                            <input type="checkbox" value="UNITED ARAB EMIRATES" checked id="country_uae">
                            <label for="country_uae">🇦🇪 UAE</label>
                        </div>
                        <div class="compact-checkbox-item">
                            <input type="checkbox" value="QATAR" checked id="country_qa">
                            <label for="country_qa">🇶🇦 Qatar</label>
                        </div>
                        <div class="compact-checkbox-item">
                            <input type="checkbox" value="KUWAIT" checked id="country_kw">
                            <label for="country_kw">🇰🇼 Kuwait</label>
                        </div>
                        <div class="compact-checkbox-item">
                            <input type="checkbox" value="OMAN" checked id="country_om">
                            <label for="country_om">🇴🇲 Oman</label>
                        </div>
                        <div class="compact-checkbox-item">
                            <input type="checkbox" value="BAHRAIN" checked id="country_bh">
                            <label for="country_bh">🇧🇭 Bahrain</label>
                        </div>
                        <div class="compact-checkbox-item">
                            <input type="checkbox" value="JORDAN" checked id="country_jo">
                            <label for="country_jo">🇯🇴 Jordan</label>
                        </div>
                        <div class="compact-checkbox-item">
                            <input type="checkbox" value="EGYPT" checked id="country_eg">
                            <label for="country_eg">🇪🇬 Egypt</label>
                        </div>
                        <div class="compact-checkbox-item">
                            <input type="checkbox" value="ISRAEL" checked id="country_il">
                            <label for="country_il">🇮🇱 Israel</label>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="filter-dropdown" id="productDropdown">
            <div class="filter-dropdown-inner">
                <div class="filter-dropdown-header">
                    <div class="filter-dropdown-title">Product Type</div>
                    <button class="filter-dropdown-close" onclick="closeFilterDropdown('product')">✕</button>
                </div>
                <div class="filter-dropdown-content">
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="productType" value="all" checked style="margin-right: 10px; cursor: pointer;" onchange="setProductType('all')">
                            <span style="font-size: 14px;">All Types</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="productType" value="SINGLE_SIDE" style="margin-right: 10px; cursor: pointer;" onchange="setProductType('SINGLE_SIDE')">
                            <span style="font-size: 14px; color: #28a745;">✓ Single Side (Artis Compatible)</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="productType" value="DOUBLE_SIDE" style="margin-right: 10px; cursor: pointer;" onchange="setProductType('DOUBLE_SIDE')">
                            <span style="font-size: 14px;">Double Side</span>
                        </label>
                    </div>
                    <input type="hidden" id="productType" value="all">
                </div>
            </div>
        </div>
        
        <div class="filter-dropdown" id="sizeDropdown">
            <div class="filter-dropdown-inner">
                <div class="filter-dropdown-header">
                    <div class="filter-dropdown-title">Size</div>
                    <button class="filter-dropdown-close" onclick="closeFilterDropdown('size')">✕</button>
                </div>
                <div class="filter-dropdown-content">
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="sizeFilter" value="all" checked style="margin-right: 10px; cursor: pointer;" onchange="setSize('all')">
                            <span style="font-size: 14px;">All Sizes</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="sizeFilter" value="1220x2440" style="margin-right: 10px; cursor: pointer;" onchange="setSize('1220x2440')">
                            <span style="font-size: 14px; color: #28a745;">✓ 1220x2440 (Artis Standard)</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="sizeFilter" value="2440x1220" style="margin-right: 10px; cursor: pointer;" onchange="setSize('2440x1220')">
                            <span style="font-size: 14px;">2440x1220</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="sizeFilter" value="other" style="margin-right: 10px; cursor: pointer;" onchange="setSize('other')">
                            <span style="font-size: 14px;">Other Sizes</span>
                        </label>
                    </div>
                    <input type="hidden" id="size" value="all">
                </div>
            </div>
        </div>
        
        <div class="filter-dropdown" id="thicknessDropdown">
            <div class="filter-dropdown-inner">
                <div class="filter-dropdown-header">
                    <div class="filter-dropdown-title">Thickness</div>
                    <button class="filter-dropdown-close" onclick="closeFilterDropdown('thickness')">✕</button>
                </div>
                <div class="filter-dropdown-content">
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="thicknessFilter" value="all" checked style="margin-right: 10px; cursor: pointer;" onchange="setThickness('all')">
                            <span style="font-size: 14px;">All Thickness</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="thicknessFilter" value="0.7" style="margin-right: 10px; cursor: pointer;" onchange="setThickness('0.7')">
                            <span style="font-size: 14px; color: #28a745;">✓ 0.7mm (Artis)</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="thicknessFilter" value="0.8" style="margin-right: 10px; cursor: pointer;" onchange="setThickness('0.8')">
                            <span style="font-size: 14px; color: #28a745;">✓ 0.8mm (Artis)</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="thicknessFilter" value="1.0" style="margin-right: 10px; cursor: pointer;" onchange="setThickness('1.0')">
                            <span style="font-size: 14px; color: #28a745;">✓ 1.0mm (Artis)</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="thicknessFilter" value="other" style="margin-right: 10px; cursor: pointer;" onchange="setThickness('other')">
                            <span style="font-size: 14px;">Other</span>
                        </label>
                    </div>
                    <input type="hidden" id="thickness" value="all">
                </div>
            </div>
        </div>
        
        <div class="filter-dropdown" id="valueDropdown">
            <div class="filter-dropdown-inner">
                <div class="filter-dropdown-header">
                    <div class="filter-dropdown-title">Minimum Order Value</div>
                    <button class="filter-dropdown-close" onclick="closeFilterDropdown('value')">✕</button>
                </div>
                <div class="filter-dropdown-content">
                    <input type="number" id="minValue" class="compact-input" value="0" min="0" placeholder="Enter minimum value in USD..." onchange="updateFilterChip('value')">
                </div>
            </div>
        </div>
        
        <div class="filter-dropdown" id="dateDropdown">
            <div class="filter-dropdown-inner">
                <div class="filter-dropdown-header">
                    <div class="filter-dropdown-title">Date Range</div>
                    <button class="filter-dropdown-close" onclick="closeFilterDropdown('date')">✕</button>
                </div>
                <div class="filter-dropdown-content">
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="dateFilter" value="all" checked style="margin-right: 10px; cursor: pointer;" onchange="setDateRange('all')">
                            <span style="font-size: 14px;">All Time (Jan 2023 - Jul 2025)</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="dateFilter" value="2025" style="margin-right: 10px; cursor: pointer;" onchange="setDateRange('2025')">
                            <span style="font-size: 14px;">2025 Only</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="dateFilter" value="2024" style="margin-right: 10px; cursor: pointer;" onchange="setDateRange('2024')">
                            <span style="font-size: 14px;">2024 Only</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="dateFilter" value="2023" style="margin-right: 10px; cursor: pointer;" onchange="setDateRange('2023')">
                            <span style="font-size: 14px;">2023 Only</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="dateFilter" value="recent" style="margin-right: 10px; cursor: pointer;" onchange="setDateRange('recent')">
                            <span style="font-size: 14px;">Last 12 Months</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="dateFilter" value="last6" style="margin-right: 10px; cursor: pointer;" onchange="setDateRange('last6')">
                            <span style="font-size: 14px;">Last 6 Months</span>
                        </label>
                        <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                            <input type="radio" name="dateFilter" value="last3" style="margin-right: 10px; cursor: pointer;" onchange="setDateRange('last3')">
                            <span style="font-size: 14px;">Last 3 Months</span>
                        </label>
                        <div>
                            <label style="display: flex; align-items: center; padding: 10px; border-radius: 8px; cursor: pointer; background: #f8f9fa; transition: all 0.2s;">
                                <input type="radio" name="dateFilter" value="custom" style="margin-right: 10px; cursor: pointer;" onchange="setDateRange('custom')">
                                <span style="font-size: 14px;">Custom Range</span>
                            </label>
                            <div id="customDatePickers" style="padding: 10px; background: #f0f4f8; border-radius: 8px; margin-top: 8px;">
                                <div style="display: flex; gap: 10px; align-items: center;">
                                    <div style="flex: 1;">
                                        <label style="font-size: 12px; color: #666; display: block; margin-bottom: 4px;">From:</label>
                                        <input type="date" id="customStartDate" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" onchange="updateCustomDateRange()">
                                    </div>
                                    <div style="flex: 1;">
                                        <label style="font-size: 12px; color: #666; display: block; margin-bottom: 4px;">To:</label>
                                        <input type="date" id="customEndDate" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" onchange="updateCustomDateRange()">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <input type="hidden" id="dateRange" value="all">
                    <input type="hidden" id="customStart" value="">
                    <input type="hidden" id="customEnd" value="">
                </div>
            </div>
        </div>
    </div>
    
    <!-- Overlay for dropdowns -->
    <div class="filter-overlay" id="filterOverlay" onclick="closeAllDropdowns()"></div>
    
    <div class="tabs">
        <button class="tab active" onclick="showTab('overview')">📊 Overview</button>
        <button class="tab" onclick="showTab('buyers')">👥 Buyer Intelligence</button>
        <button class="tab" onclick="showTab('products')">📦 Product Analysis</button>
        <button class="tab" onclick="showTab('competitors')">🏢 Competitors</button>
        <button class="tab" onclick="showTab('pricing')">💰 Pricing</button>
        <button class="tab" onclick="showTab('insights')">💡 Key Insights</button>
    </div>
    
    <div class="content">
        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="loading">Loading overview data...</div>
        </div>
        
        <!-- Buyer Intelligence Tab -->
        <div id="buyers" class="tab-content">
            <div class="loading">Loading buyer intelligence...</div>
        </div>
        
        <!-- Product Analysis Tab -->
        <div id="products" class="tab-content">
            <div class="loading">Loading product analysis...</div>
        </div>
        
        <!-- Competitors Tab -->
        <div id="competitors" class="tab-content">
            <div class="loading">Loading competitor data...</div>
        </div>
        
        <!-- Pricing Tab -->
        <div id="pricing" class="tab-content">
            <div class="loading">Loading pricing analysis...</div>
        </div>
        
        <!-- Insights Tab -->
        <div id="insights" class="tab-content">
            <div class="loading">Loading key insights...</div>
        </div>
    </div>
    
    <script>
        let currentTab = 'overview';
        let currentFilters = {};
        let activeDropdown = null;
        
        function showTab(tabName) {
            // Update tabs
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            currentTab = tabName;
            loadTabData(tabName);
        }
        
        function toggleFilterDropdown(filterName) {
            const dropdown = document.getElementById(filterName + 'Dropdown');
            const overlay = document.getElementById('filterOverlay');
            
            if (activeDropdown && activeDropdown !== dropdown) {
                activeDropdown.classList.remove('active');
            }
            
            dropdown.classList.toggle('active');
            overlay.classList.toggle('active', dropdown.classList.contains('active'));
            
            activeDropdown = dropdown.classList.contains('active') ? dropdown : null;
        }
        
        function closeFilterDropdown(filterName) {
            const dropdown = document.getElementById(filterName + 'Dropdown');
            const overlay = document.getElementById('filterOverlay');
            dropdown.classList.remove('active');
            overlay.classList.remove('active');
            activeDropdown = null;
        }
        
        function closeAllDropdowns() {
            document.querySelectorAll('.filter-dropdown').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
            document.getElementById('filterOverlay').classList.remove('active');
            activeDropdown = null;
        }
        
        function setProductType(value) {
            document.getElementById('productType').value = value;
            updateFilterChip('product');
            closeFilterDropdown('product');
        }
        
        function setSize(value) {
            document.getElementById('size').value = value;
            updateFilterChip('size');
            closeFilterDropdown('size');
        }
        
        function setThickness(value) {
            document.getElementById('thickness').value = value;
            updateFilterChip('thickness');
            closeFilterDropdown('thickness');
        }
        
        function setDateRange(value) {
            document.getElementById('dateRange').value = value;
            
            // Show/hide custom date pickers
            const customPickers = document.getElementById('customDatePickers');
            if (value === 'custom') {
                customPickers.style.display = 'block';
                // Keep dropdown open for custom option
                return;
            } else {
                customPickers.style.display = 'none';
                updateFilterChip('date');
                closeFilterDropdown('date');
            }
        }
        
        function updateCustomDateRange() {
            const startDate = document.getElementById('customStartDate').value;
            const endDate = document.getElementById('customEndDate').value;
            
            if (startDate && endDate) {
                document.getElementById('customStart').value = startDate;
                document.getElementById('customEnd').value = endDate;
                updateFilterChip('date');
                // Optionally close dropdown after both dates are selected
                setTimeout(() => closeFilterDropdown('date'), 500);
            }
        }
        
        function updateFilterChip(filterName) {
            const chipValue = document.getElementById(filterName + 'Value');
            const chip = document.getElementById(filterName + 'Chip');
            
            if (filterName === 'countries') {
                const checked = document.querySelectorAll('#countryCheckboxes input:checked').length;
                const total = document.querySelectorAll('#countryCheckboxes input').length;
                chipValue.textContent = checked === total ? 'All' : `${checked} selected`;
                chip.classList.toggle('active', checked < total);
            } else if (filterName === 'product') {
                const value = document.getElementById('productType').value;
                chipValue.textContent = value === 'all' ? 'All' : 
                    value === 'SINGLE_SIDE' ? 'Single' : 'Double';
                chip.classList.toggle('active', value !== 'all');
            } else if (filterName === 'size') {
                const value = document.getElementById('size').value;
                chipValue.textContent = value === 'all' ? 'All' : 
                    value === '1220x2440' ? '1220x2440' : 
                    value === '2440x1220' ? '2440x1220' : 'Other';
                chip.classList.toggle('active', value !== 'all');
            } else if (filterName === 'thickness') {
                const value = document.getElementById('thickness').value;
                chipValue.textContent = value === 'all' ? 'All' : 
                    value === 'other' ? 'Other' : `${value}mm`;
                chip.classList.toggle('active', value !== 'all');
            } else if (filterName === 'value') {
                const value = document.getElementById('minValue').value;
                chipValue.textContent = value > 0 ? `$${parseInt(value).toLocaleString()}` : '$0';
                chip.classList.toggle('active', value > 0);
            } else if (filterName === 'date') {
                const value = document.getElementById('dateRange').value;
                const labels = {
                    'all': 'All Time',
                    '2025': '2025',
                    '2024': '2024',
                    '2023': '2023',
                    'recent': 'Last 12M',
                    'last6': 'Last 6M',
                    'last3': 'Last 3M',
                    'custom': 'Custom'
                };
                
                if (value === 'custom') {
                    const startDate = document.getElementById('customStart').value;
                    const endDate = document.getElementById('customEnd').value;
                    if (startDate && endDate) {
                        const start = new Date(startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                        const end = new Date(endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                        chipValue.textContent = `${start} - ${end}`;
                    } else {
                        chipValue.textContent = 'Custom';
                    }
                } else {
                    chipValue.textContent = labels[value] || 'All Time';
                }
                chip.classList.toggle('active', value !== 'all');
            }
        }
        
        function getFilters() {
            const selectedCountries = [];
            document.querySelectorAll('#countryCheckboxes input[type="checkbox"]:checked').forEach(cb => {
                selectedCountries.push(cb.value);
            });
            
            let countries = null;
            if (!selectedCountries.includes('all') && selectedCountries.length > 0) {
                countries = selectedCountries;
            }
            
            const dateRange = document.getElementById('dateRange').value;
            const filters = {
                countries: countries,
                productType: document.getElementById('productType').value,
                size: document.getElementById('size').value,
                thickness: document.getElementById('thickness').value,
                minValue: document.getElementById('minValue').value,
                dateRange: dateRange
            };
            
            // Add custom date range if selected
            if (dateRange === 'custom') {
                filters.customStart = document.getElementById('customStart').value;
                filters.customEnd = document.getElementById('customEnd').value;
            }
            
            return filters;
        }
        
        function applyFilters() {
            currentFilters = getFilters();
            loadTabData(currentTab);
            closeAllDropdowns();
            
            // Update all filter chips
            updateFilterChip('countries');
            updateFilterChip('product');
            updateFilterChip('size');
            updateFilterChip('thickness');
            updateFilterChip('value');
            updateFilterChip('date');
        }
        
        async function loadTabData(tabName) {
            const params = new URLSearchParams();
            if (currentFilters.countries) {
                currentFilters.countries.forEach(c => params.append('countries', c));
            }
            if (currentFilters.productType !== 'all') {
                params.append('product_type', currentFilters.productType);
            }
            if (currentFilters.size !== 'all') {
                params.append('size', currentFilters.size);
            }
            if (currentFilters.thickness !== 'all') {
                params.append('thickness', currentFilters.thickness);
            }
            if (currentFilters.minValue) {
                params.append('min_value', currentFilters.minValue);
            }
            if (currentFilters.dateRange !== 'all') {
                params.append('date_range', currentFilters.dateRange);
                
                // Add custom date parameters if custom range is selected
                if (currentFilters.dateRange === 'custom') {
                    if (currentFilters.customStart) {
                        params.append('custom_start', currentFilters.customStart);
                    }
                    if (currentFilters.customEnd) {
                        params.append('custom_end', currentFilters.customEnd);
                    }
                }
            }
            
            try {
                const response = await fetch(`/api/${tabName}?${params}`);
                const data = await response.json();
                renderTabContent(tabName, data);
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById(tabName).innerHTML = '<div class="loading">Error loading data</div>';
            }
        }
        
        function renderTabContent(tabName, data) {
            const container = document.getElementById(tabName);
            
            switch(tabName) {
                case 'overview':
                    renderOverview(container, data);
                    break;
                case 'buyers':
                    renderBuyers(container, data);
                    break;
                case 'products':
                    renderProducts(container, data);
                    break;
                case 'competitors':
                    renderCompetitors(container, data);
                    break;
                case 'pricing':
                    renderPricing(container, data);
                    break;
                case 'insights':
                    renderInsights(container, data);
                    break;
            }
        }
        
        function renderOverview(container, data) {
            container.innerHTML = `
                <h2>Market Overview</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Total Market Value</div>
                        <div class="stat-value">$${(data.total_value / 1000000).toFixed(1)}M</div>
                        <div class="stat-label">${data.total_shipments.toLocaleString()} shipments</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                        <div class="stat-label">Single-Side Market</div>
                        <div class="stat-value">${data.single_side_pct}%</div>
                        <div class="stat-label">${data.single_side_count.toLocaleString()} orders</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #dc3545 0%, #f86734 100%);">
                        <div class="stat-label">Active Buyers</div>
                        <div class="stat-value">${data.unique_buyers}</div>
                        <div class="stat-label">Importing regularly</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #ffc107 0%, #ff6b6b 100%);">
                        <div class="stat-label">Avg Order Value</div>
                        <div class="stat-value">$${data.avg_order_value.toFixed(0)}</div>
                        <div class="stat-label">Per shipment</div>
                    </div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="margin: 0;">Country Distribution</h3>
                        <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px;">
                            <span style="font-size: 15px; font-weight: 600; color: #444;">View by:</span>
                            <button id="valueBtn" onclick="setMetric('value')" style="padding: 10px 28px; background: #1a237e; color: white; border: none; border-radius: 6px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.2s;">
                                Value (USD)
                            </button>
                            <button id="volumeBtn" onclick="setMetric('volume')" style="padding: 10px 28px; background: white; color: #555; border: 2px solid #ddd; border-radius: 6px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.2s;">
                                Volume (Sheets)
                            </button>
                        </div>
                    </div>
                    <div style="position: relative; height: 350px; overflow-x: auto; overflow-y: hidden;">
                        <div style="min-width: ${Math.max(600, data.country_dist.labels.length * 80)}px; height: 320px;">
                            <canvas id="countryChart"></canvas>
                        </div>
                    </div>
                </div>
            `;
            
            // Store country data globally for toggle
            window.countryData = data.country_dist;
            
            // Render chart with proper cleanup
            if (data.country_dist && data.country_dist.labels && data.country_dist.labels.length > 0) {
                setTimeout(() => {
                    // Destroy existing chart if any
                    if (window.countryChartInstance) {
                        window.countryChartInstance.destroy();
                    }
                    renderCountryChart(data.country_dist);
                }, 100);
            }
        }
        
        function renderBuyers(container, data) {
            let html = `
                <h2>Top Buyers Intelligence</h2>
                <p style="margin-bottom: 20px; color: #666;">
                    Found ${data.total_buyers} buyers | 
                    Single-side buyers: ${data.single_side_buyers} | 
                    Target opportunities: ${data.artis_compatible_buyers}
                </p>
            `;
            
            data.buyers.forEach(buyer => {
                const buyerClass = buyer.single_side_pct > 70 ? 'single-side-buyer' : 
                                  buyer.single_side_pct < 30 ? 'double-side-buyer' : 'mixed-buyer';
                
                const isArtisTarget = buyer.buys_1220x2440 && buyer.single_side_pct > 50;
                
                html += `
                    <div class="buyer-card ${buyerClass}">
                        <div class="buyer-name">
                            ${buyer.name} 
                            ${isArtisTarget ? '<span class="highlight">🎯 Artis Target</span>' : ''}
                        </div>
                        <div class="buyer-details">
                            <div class="buyer-stat">
                                <span class="buyer-stat-label">Country</span>
                                <span class="buyer-stat-value">${buyer.countries}</span>
                            </div>
                            <div class="buyer-stat">
                                <span class="buyer-stat-label">Total Orders</span>
                                <span class="buyer-stat-value">${buyer.total_orders}</span>
                            </div>
                            <div class="buyer-stat">
                                <span class="buyer-stat-label">Total Value</span>
                                <span class="buyer-stat-value">$${(buyer.total_value / 1000).toFixed(0)}K</span>
                            </div>
                            <div class="buyer-stat">
                                <span class="buyer-stat-label">Single-Side %</span>
                                <span class="buyer-stat-value">${buyer.single_side_pct}%</span>
                            </div>
                            <div class="buyer-stat">
                                <span class="buyer-stat-label">Avg Price/Unit</span>
                                <span class="buyer-stat-value">$${buyer.avg_price.toFixed(2)}</span>
                            </div>
                            <div class="buyer-stat">
                                <span class="buyer-stat-label">Main Supplier</span>
                                <span class="buyer-stat-value">${buyer.main_supplier}</span>
                            </div>
                            <div class="buyer-stat">
                                <span class="buyer-stat-label">Sizes Ordered</span>
                                <span class="buyer-stat-value">${buyer.sizes || 'Various'}</span>
                            </div>
                            <div class="buyer-stat">
                                <span class="buyer-stat-label">Last Order</span>
                                <span class="buyer-stat-value">${buyer.last_order}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        function renderProducts(container, data) {
            container.innerHTML = `
                <h2>Product Specification Analysis</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Most Common Size</div>
                        <div class="stat-value">${data.top_size}</div>
                        <div class="stat-label">${data.top_size_pct}% of market</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                        <div class="stat-label">Artis Size (1220x2440)</div>
                        <div class="stat-value">${data.artis_size_pct}%</div>
                        <div class="stat-label">Market share</div>
                    </div>
                </div>
                
                <div class="table-container">
                    <h3>Size Distribution</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Size (mm)</th>
                                <th>Orders</th>
                                <th>Market %</th>
                                <th>Single-Side %</th>
                                <th>Avg Price</th>
                                <th>Top Buyers</th>
                            </tr>
                        </thead>
                        <tbody id="sizeTable"></tbody>
                    </table>
                </div>
                
                <div class="table-container">
                    <h3>Thickness Distribution</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Thickness (mm)</th>
                                <th>Orders</th>
                                <th>Market %</th>
                                <th>Single-Side %</th>
                                <th>Avg Price</th>
                            </tr>
                        </thead>
                        <tbody id="thicknessTable"></tbody>
                    </table>
                </div>
            `;
            
            // Populate tables
            if (data.sizes) {
                const sizeTable = document.getElementById('sizeTable');
                data.sizes.forEach(size => {
                    sizeTable.innerHTML += `
                        <tr>
                            <td>${size.size}</td>
                            <td>${size.count}</td>
                            <td>${size.pct}%</td>
                            <td>${size.single_side_pct}%</td>
                            <td>$${size.avg_price}</td>
                            <td>${size.top_buyers}</td>
                        </tr>
                    `;
                });
            }
            
            if (data.thickness) {
                const thicknessTable = document.getElementById('thicknessTable');
                data.thickness.forEach(thick => {
                    thicknessTable.innerHTML += `
                        <tr>
                            <td>${thick.thickness}</td>
                            <td>${thick.count}</td>
                            <td>${thick.pct}%</td>
                            <td>${thick.single_side_pct}%</td>
                            <td>$${thick.avg_price}</td>
                        </tr>
                    `;
                });
            }
        }
        
        function renderCompetitors(container, data) {
            // Store data globally for toggle
            window.competitorData = data;
            
            container.innerHTML = `
                <h2>Competitor Analysis</h2>
                <div class="chart-container">
                    <h3>Market Share by Supplier (Value-based)</h3>
                    <canvas id="supplierChart"></canvas>
                </div>
                
                <div class="table-container">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="margin: 0;">Top Competitors</h3>
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 6px; display: flex; align-items: center; justify-content: center; gap: 12px;">
                            <span style="font-size: 14px; font-weight: 600; color: #444;">View by:</span>
                            <button id="compValueBtn" onclick="setCompetitorMetric('value')" style="padding: 8px 20px; background: #1a237e; color: white; border: none; border-radius: 5px; font-size: 14px; font-weight: 600; cursor: pointer;">
                                Value
                            </button>
                            <button id="compVolumeBtn" onclick="setCompetitorMetric('volume')" style="padding: 8px 20px; background: white; color: #555; border: 2px solid #ddd; border-radius: 5px; font-size: 14px; font-weight: 600; cursor: pointer;">
                                Volume
                            </button>
                        </div>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Supplier</th>
                                <th>Origin</th>
                                <th>Orders</th>
                                <th>Total Value</th>
                                <th id="marketShareHeader">Market Share (Value)</th>
                                <th>Single-Side %</th>
                                <th>Avg Price</th>
                                <th>Top Markets</th>
                                <th>Key Buyers</th>
                            </tr>
                        </thead>
                        <tbody id="competitorTableBody">
                            ${data.competitors.map(comp => `
                                <tr>
                                    <td><strong>${comp.name}</strong></td>
                                    <td>${comp.country}</td>
                                    <td>${comp.orders}</td>
                                    <td>$${(comp.total_value/1000000).toFixed(1)}M</td>
                                    <td class="market-share-cell">${comp.market_share_value}%</td>
                                    <td>${comp.single_side_pct}%</td>
                                    <td>$${comp.avg_price}</td>
                                    <td style="color: #667eea; font-weight: 600;">${comp.top_countries || 'N/A'}</td>
                                    <td>${comp.key_buyers}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            
            if (data.supplier_chart) {
                renderSupplierChart(data.supplier_chart);
            }
        }
        
        function renderPricing(container, data) {
            container.innerHTML = `
                <h2>Pricing Analysis</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Single-Side Avg Price</div>
                        <div class="stat-value">$${data.single_side_avg}</div>
                        <div class="stat-label">Per unit</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #dc3545 0%, #f86734 100%);">
                        <div class="stat-label">Double-Side Avg Price</div>
                        <div class="stat-value">$${data.double_side_avg}</div>
                        <div class="stat-label">Per unit</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>Price Distribution by Product Type</h3>
                    <canvas id="priceChart"></canvas>
                </div>
                
                <div class="table-container">
                    <h3>Price Ranges by Specification</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Specification</th>
                                <th>Min Price</th>
                                <th>Avg Price</th>
                                <th>Max Price</th>
                                <th>Most Common</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.price_ranges.map(range => `
                                <tr>
                                    <td>${range.spec}</td>
                                    <td>$${range.min}</td>
                                    <td>$${range.avg}</td>
                                    <td>$${range.max}</td>
                                    <td>$${range.mode}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            
            if (data.price_chart) {
                renderPriceChart(data.price_chart);
            }
        }
        
        function renderInsights(container, data) {
            container.innerHTML = `
                <h2>Key Insights & Recommendations</h2>
                
                <div style="background: #d4edda; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h3>✅ Opportunities for Artis</h3>
                    <ul style="margin-top: 10px; line-height: 1.8;">
                        ${data.opportunities.map(opp => `<li>${opp}</li>`).join('')}
                    </ul>
                </div>
                
                <div style="background: #f8d7da; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h3>⚠️ Challenges to Address</h3>
                    <ul style="margin-top: 10px; line-height: 1.8;">
                        ${data.challenges.map(ch => `<li>${ch}</li>`).join('')}
                    </ul>
                </div>
                
                <div style="background: #cfe2ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h3>🎯 Priority Actions</h3>
                    <ol style="margin-top: 10px; line-height: 1.8;">
                        ${data.actions.map(action => `<li><strong>${action.title}</strong>: ${action.detail}</li>`).join('')}
                    </ol>
                </div>
                
                <div style="background: #fff3cd; padding: 20px; border-radius: 10px;">
                    <h3>📊 Market Summary</h3>
                    <p>${data.summary}</p>
                </div>
            `;
        }
        
        function renderTrendsChart(trends) {
            const ctx = document.getElementById('trendsChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: trends.labels,
                    datasets: [{
                        label: 'Single-Side Orders',
                        data: trends.single_side,
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Double-Side Orders',
                        data: trends.double_side,
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function setMetric(metric) {
            // Update button styles
            const volumeBtn = document.getElementById('volumeBtn');
            const valueBtn = document.getElementById('valueBtn');
            
            if (metric === 'volume') {
                volumeBtn.style.background = '#1a237e';
                volumeBtn.style.color = 'white';
                volumeBtn.style.border = 'none';
                valueBtn.style.background = 'white';
                valueBtn.style.color = '#555';
                valueBtn.style.border = '2px solid #ddd';
            } else {
                valueBtn.style.background = '#1a237e';
                valueBtn.style.color = 'white';
                valueBtn.style.border = 'none';
                volumeBtn.style.background = 'white';
                volumeBtn.style.color = '#555';
                volumeBtn.style.border = '2px solid #ddd';
            }
            
            window.currentMetric = metric;
            updateCountryChart();
        }
        
        function updateCountryChart() {
            if (window.countryData) {
                if (window.countryChartInstance) {
                    window.countryChartInstance.destroy();
                }
                renderCountryChart(window.countryData);
            }
        }
        
        // Store competitor data globally
        window.competitorData = null;
        
        function setCompetitorMetric(metric) {
            const valueBtn = document.getElementById('compValueBtn');
            const volumeBtn = document.getElementById('compVolumeBtn');
            const header = document.getElementById('marketShareHeader');
            
            if (metric === 'value') {
                valueBtn.style.background = '#1a237e';
                valueBtn.style.color = 'white';
                valueBtn.style.border = 'none';
                volumeBtn.style.background = 'white';
                volumeBtn.style.color = '#555';
                volumeBtn.style.border = '2px solid #ddd';
                header.textContent = 'Market Share (Value)';
            } else {
                volumeBtn.style.background = '#1a237e';
                volumeBtn.style.color = 'white';
                volumeBtn.style.border = 'none';
                valueBtn.style.background = 'white';
                valueBtn.style.color = '#555';
                valueBtn.style.border = '2px solid #ddd';
                header.textContent = 'Market Share (Volume)';
            }
            
            // Update market share cells
            if (window.competitorData) {
                const cells = document.querySelectorAll('.market-share-cell');
                window.competitorData.competitors.forEach((comp, index) => {
                    if (cells[index]) {
                        cells[index].textContent = metric === 'value' ? 
                            comp.market_share_value + '%' : 
                            comp.market_share_volume + '%';
                    }
                });
                
                // Update pie chart
                if (window.supplierChartInstance) {
                    window.supplierChartInstance.destroy();
                }
                
                // Re-render chart with new metric
                const chartData = {
                    labels: window.competitorData.competitors.slice(0, 10).map(c => c.name.substring(0, 20)),
                    values: window.competitorData.competitors.slice(0, 10).map(c => 
                        metric === 'value' ? c.market_share_value : c.market_share_volume
                    )
                };
                renderSupplierChart(chartData);
                
                // Update chart title
                const chartTitle = document.querySelector('.chart-container h3');
                if (chartTitle) {
                    chartTitle.textContent = metric === 'value' ? 
                        'Market Share by Supplier (Value-based)' : 
                        'Market Share by Supplier (Volume-based)';
                }
            }
        }
        
        function renderSupplierChart(data) {
            const ctx = document.getElementById('supplierChart').getContext('2d');
            window.supplierChartInstance = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            '#667eea', '#764ba2', '#28a745', '#ffc107', 
                            '#dc3545', '#17a2b8', '#6610f2', '#e83e8c',
                            '#fd7e14', '#20c997'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.label + ': ' + context.parsed + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function renderPriceChart(data) {
            // Placeholder for price chart if needed
        }
        
        function renderCountryChart(data) {
            const metric = window.currentMetric || 'volume';
            const values = metric === 'value' ? data.value_pct : data.volume_pct;
            const label = metric === 'value' ? 'Market Share by Value (%)' : 'Market Share by Volume (Sheets %)';
            
            const ctx = document.getElementById('countryChart').getContext('2d');
            
            // Simple, professional colors
            const colors = [
                '#667eea', '#764ba2', '#28a745', '#ffc107', '#dc3545', 
                '#17a2b8', '#6610f2', '#e83e8c', '#fd7e14', '#20c997',
                '#6c757d', '#343a40', '#007bff', '#6f42c1', '#e74c3c'
            ];
            
            window.countryChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels.map(label => {
                        // Shorten country names for better display
                        const shortNames = {
                            'UNITED ARAB EMIRATES': 'UAE',
                            'SAUDI ARABIA': 'Saudi Arabia'
                        };
                        return shortNames[label] || label;
                    }),
                    datasets: [{
                        label: label,
                        data: values,
                        backgroundColor: colors,
                        borderRadius: 5,
                        barThickness: 40,
                        maxBarThickness: 50
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            titleFont: {
                                size: 14,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 13
                            },
                            callbacks: {
                                label: function(context) {
                                    return context.parsed.y.toFixed(1) + '% of total market';
                                },
                                afterLabel: function(context) {
                                    const actualValue = metric === 'value' ? 
                                        'Value: $' + (context.parsed.y * 2.5).toFixed(1) + 'M' :
                                        'Volume: ' + (context.parsed.y * 100000).toFixed(0) + ' sheets';
                                    return actualValue;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: {
                                    size: 11,
                                    weight: '600'
                                },
                                color: '#495057',
                                autoSkip: false,
                                maxRotation: 45,
                                minRotation: 45
                            }
                        },
                        y: {
                            beginAtZero: true,
                            max: Math.max(...values) + 5,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                font: {
                                    size: 11
                                },
                                color: '#6c757d',
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Select All functionality
        document.getElementById('selectAll').addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('#countryCheckboxes input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
        
        // Update Select All when individual checkboxes change
        document.querySelectorAll('#countryCheckboxes input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', function() {
                const allCheckboxes = document.querySelectorAll('#countryCheckboxes input[type="checkbox"]');
                const checkedBoxes = document.querySelectorAll('#countryCheckboxes input[type="checkbox"]:checked');
                document.getElementById('selectAll').checked = allCheckboxes.length === checkedBoxes.length;
            });
        });
        
        // Add hover effect to checkbox labels
        document.querySelectorAll('#countryCheckboxes label').forEach(label => {
            label.addEventListener('mouseenter', function() {
                this.style.background = '#f5f5f5';
            });
            label.addEventListener('mouseleave', function() {
                this.style.background = 'transparent';
            });
        });
        
        // Export functionality
        function exportToExcel() {
            const activeTab = document.querySelector('.tab-button.active').textContent.toLowerCase();
            alert('Export functionality will be available soon! Current tab: ' + activeTab);
            // You can implement actual export here by calling an API endpoint
        }
        
        // Initialize
        window.onload = () => {
            // Hide custom date pickers initially
            document.getElementById('customDatePickers').style.display = 'none';
            
            // Initialize country checkboxes event listeners
            document.getElementById('selectAll').addEventListener('change', function() {
                const checkboxes = document.querySelectorAll('#countryCheckboxes input[type="checkbox"]');
                checkboxes.forEach(cb => cb.checked = this.checked);
                updateFilterChip('countries');
            });
            
            document.querySelectorAll('#countryCheckboxes input[type="checkbox"]').forEach(cb => {
                cb.addEventListener('change', () => {
                    updateFilterChip('countries');
                    // Update select all checkbox
                    const allChecked = document.querySelectorAll('#countryCheckboxes input[type="checkbox"]:checked').length === 
                                      document.querySelectorAll('#countryCheckboxes input[type="checkbox"]').length;
                    document.getElementById('selectAll').checked = allChecked;
                });
            });
            
            // Initialize filter chip values
            updateFilterChip('countries');
            updateFilterChip('product');
            updateFilterChip('size');
            updateFilterChip('thickness');
            updateFilterChip('value');
            updateFilterChip('date');
            
            applyFilters();
        };
    </script>
</body>
</html>
"""

@app.get("/api/overview")
async def get_overview(
    countries: List[str] = Query(None),
    product_type: Optional[str] = None,
    size: Optional[str] = None,
    thickness: Optional[str] = None,
    min_value: Optional[float] = None,
    date_range: Optional[str] = None,
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None
):
    """Get overview statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    if countries:
        placeholders = ','.join(['?' for _ in countries])
        where_conditions.append(f"DESTINATION_COUNTRY IN ({placeholders})")
        params.extend(countries)
    
    if product_type and product_type != 'all':
        where_conditions.append("PRODUCT_TYPE = ?")
        params.append(product_type)
    
    if size and size != 'all':
        if size == '1220x2440':
            where_conditions.append("(SIZE = '2440x1220' OR SIZE = '1220x2440')")
        elif size == 'other':
            where_conditions.append("(SIZE != '2440x1220' AND SIZE != '1220x2440')")
        else:
            where_conditions.append("SIZE = ?")
            params.append(size)
    
    if thickness and thickness != 'all':
        if thickness == 'other':
            where_conditions.append("(THICKNESS NOT IN (0.7, 0.8, 1.0) OR THICKNESS IS NULL)")
        else:
            where_conditions.append("THICKNESS = ?")
            params.append(float(thickness))
    
    if min_value:
        where_conditions.append("TOTAL_VALUE_USD >= ?")
        params.append(min_value)
    
    if date_range and date_range != 'all':
        if date_range == 'custom' and custom_start and custom_end:
            where_conditions.append(f"DATE BETWEEN '{custom_start}' AND '{custom_end}'")
        elif date_range == '2025':
            where_conditions.append("DATE >= '2025-01-01'")
        elif date_range == '2024':
            where_conditions.append("DATE BETWEEN '2024-01-01' AND '2024-12-31'")
        elif date_range == '2023':
            where_conditions.append("DATE BETWEEN '2023-01-01' AND '2023-12-31'")
        elif date_range == 'recent':
            where_conditions.append("DATE >= date('now', '-12 months')")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # Get statistics
    query = f"""
        SELECT 
            COUNT(*) as total_shipments,
            SUM(TOTAL_VALUE_USD) as total_value,
            COUNT(DISTINCT CONSIGNEE_NAME) as unique_buyers,
            AVG(TOTAL_VALUE_USD) as avg_order_value,
            SUM(CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 ELSE 0 END) as single_side_count,
            ROUND(SUM(CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as single_side_pct
        FROM mirror_shipments
        WHERE {where_clause}
    """
    
    cursor.execute(query, params)
    stats = cursor.fetchone()
    
    # Get country distribution by volume (sheets) and value - show all countries
    country_query = f"""
        SELECT 
            DESTINATION_COUNTRY,
            SUM(QUANTITY) as total_sheets,
            ROUND(SUM(QUANTITY) * 100.0 / (SELECT SUM(QUANTITY) FROM mirror_shipments WHERE {where_clause}), 1) as volume_pct,
            SUM(TOTAL_VALUE_USD) as total_value,
            ROUND(SUM(TOTAL_VALUE_USD) * 100.0 / (SELECT SUM(TOTAL_VALUE_USD) FROM mirror_shipments WHERE {where_clause}), 1) as value_pct
        FROM mirror_shipments
        WHERE {where_clause}
        GROUP BY DESTINATION_COUNTRY
        ORDER BY total_value DESC
        LIMIT 15
    """
    
    # Need to triple the params for the three WHERE clauses in the query (main + 2 subqueries)
    cursor.execute(country_query, params + params + params)
    country_data = cursor.fetchall()
    
    conn.close()
    
    return {
        "total_shipments": stats[0] or 0,
        "total_value": stats[1] or 0,
        "unique_buyers": stats[2] or 0,
        "avg_order_value": stats[3] or 0,
        "single_side_count": stats[4] or 0,
        "single_side_pct": stats[5] or 0,
        "country_dist": {
            "labels": [row[0] for row in country_data],
            "volume_pct": [row[2] for row in country_data],
            "value_pct": [row[4] for row in country_data],
            "values": [row[2] for row in country_data]  # Default to volume for backward compatibility
        }
    }

@app.get("/api/buyers")
async def get_buyers(
    countries: List[str] = Query(None),
    product_type: Optional[str] = None,
    size: Optional[str] = None,
    thickness: Optional[str] = None,
    min_value: Optional[float] = None,
    date_range: Optional[str] = None,
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None
):
    """Get buyer intelligence"""
    conn = get_db_connection()
    
    # Build WHERE clause
    where_conditions = ["CONSIGNEE_NAME NOT LIKE '%ORDER%'"]
    params = []
    
    if countries:
        placeholders = ','.join(['?' for _ in countries])
        where_conditions.append(f"DESTINATION_COUNTRY IN ({placeholders})")
        params.extend(countries)
    
    if product_type and product_type != 'all':
        where_conditions.append("PRODUCT_TYPE = ?")
        params.append(product_type)
    
    if size and size != 'all':
        if size == '1220x2440':
            where_conditions.append("(SIZE = '2440x1220' OR SIZE = '1220x2440')")
        elif size == 'other':
            where_conditions.append("(SIZE != '2440x1220' AND SIZE != '1220x2440')")
    
    if thickness and thickness != 'all':
        if thickness != 'other':
            where_conditions.append("THICKNESS = ?")
            params.append(float(thickness))
    
    if min_value:
        where_conditions.append("TOTAL_VALUE_USD >= ?")
        params.append(min_value)
    
    # Add date range filter
    if date_range and date_range != 'all':
        if date_range == 'custom' and custom_start and custom_end:
            where_conditions.append(f"DATE BETWEEN '{custom_start}' AND '{custom_end}'")
        elif date_range == '2025':
            where_conditions.append("DATE >= '2025-01-01'")
        elif date_range == '2024':
            where_conditions.append("DATE BETWEEN '2024-01-01' AND '2024-12-31'")
        elif date_range == '2023':
            where_conditions.append("DATE BETWEEN '2023-01-01' AND '2023-12-31'")
        elif date_range == 'recent':
            where_conditions.append("DATE >= date('now', '-12 months')")
        elif date_range == 'last6':
            where_conditions.append("DATE >= date('now', '-6 months')")
        elif date_range == 'last3':
            where_conditions.append("DATE >= date('now', '-3 months')")
    
    where_clause = " AND ".join(where_conditions)
    
    # Get top buyers
    query = f"""
        SELECT 
            CONSIGNEE_NAME,
            GROUP_CONCAT(DISTINCT DESTINATION_COUNTRY) as countries,
            COUNT(*) as total_orders,
            SUM(TOTAL_VALUE_USD) as total_value,
            SUM(CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 ELSE 0 END) as single_side,
            ROUND(SUM(CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as single_side_pct,
            AVG(UNIT_PRICE_USD) as avg_price,
            GROUP_CONCAT(DISTINCT SHIPPER_NAME) as suppliers,
            GROUP_CONCAT(DISTINCT SIZE) as sizes,
            MAX(DATE) as last_order,
            SUM(CASE WHEN SIZE IN ('1220x2440', '2440x1220') THEN 1 ELSE 0 END) as buys_1220x2440
        FROM mirror_shipments
        WHERE {where_clause}
        GROUP BY CONSIGNEE_NAME
        ORDER BY total_value DESC
        LIMIT 50
    """
    
    cursor = conn.cursor()
    cursor.execute(query, params)
    buyers = cursor.fetchall()
    
    # Get total counts
    count_query = f"""
        SELECT 
            COUNT(DISTINCT CONSIGNEE_NAME) as total_buyers,
            COUNT(DISTINCT CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN CONSIGNEE_NAME END) as single_side_buyers
        FROM mirror_shipments
        WHERE {where_clause}
    """
    
    cursor.execute(count_query, params)
    counts = cursor.fetchone()
    
    conn.close()
    
    buyer_list = []
    artis_compatible = 0
    
    for buyer in buyers:
        # Extract main supplier
        suppliers = buyer[7].split(',') if buyer[7] else []
        main_supplier = suppliers[0] if suppliers else 'Unknown'
        
        # Check if Artis compatible
        if buyer[10] > 0 and buyer[5] > 50:  # Buys 1220x2440 and >50% single-side
            artis_compatible += 1
        
        buyer_list.append({
            "name": buyer[0],
            "countries": buyer[1],
            "total_orders": buyer[2],
            "total_value": buyer[3] or 0,
            "single_side": buyer[4],
            "single_side_pct": buyer[5] or 0,
            "avg_price": buyer[6] or 0,
            "main_supplier": main_supplier,
            "sizes": buyer[8] if buyer[8] else 'Various',
            "last_order": buyer[9],
            "buys_1220x2440": buyer[10] > 0
        })
    
    return {
        "total_buyers": counts[0],
        "single_side_buyers": counts[1],
        "artis_compatible_buyers": artis_compatible,
        "buyers": buyer_list
    }

@app.get("/api/products")
async def get_products(
    countries: List[str] = Query(None),
    product_type: Optional[str] = None,
    min_value: Optional[float] = None,
    size: Optional[str] = None,
    thickness: Optional[str] = None,
    date_range: Optional[str] = None,
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None
):
    """Get product specification analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    if countries:
        placeholders = ','.join(['?' for _ in countries])
        where_conditions.append(f"DESTINATION_COUNTRY IN ({placeholders})")
        params.extend(countries)
    
    if product_type and product_type != 'all':
        where_conditions.append("PRODUCT_TYPE = ?")
        params.append(product_type)
    
    if size and size != 'all':
        if size == '1220x2440':
            where_conditions.append("(SIZE = '2440x1220' OR SIZE = '1220x2440')")
        elif size == 'other':
            where_conditions.append("(SIZE != '2440x1220' AND SIZE != '1220x2440')")
    
    if thickness and thickness != 'all':
        if thickness != 'other':
            where_conditions.append("THICKNESS = ?")
            params.append(float(thickness))
    
    if min_value:
        where_conditions.append("TOTAL_VALUE_USD >= ?")
        params.append(min_value)
    
    # Add date range filter
    if date_range and date_range != 'all':
        if date_range == 'custom' and custom_start and custom_end:
            where_conditions.append(f"DATE BETWEEN '{custom_start}' AND '{custom_end}'")
        elif date_range == '2025':
            where_conditions.append("DATE >= '2025-01-01'")
        elif date_range == '2024':
            where_conditions.append("DATE BETWEEN '2024-01-01' AND '2024-12-31'")
        elif date_range == '2023':
            where_conditions.append("DATE BETWEEN '2023-01-01' AND '2023-12-31'")
        elif date_range == 'recent':
            where_conditions.append("DATE >= date('now', '-12 months')")
        elif date_range == 'last6':
            where_conditions.append("DATE >= date('now', '-6 months')")
        elif date_range == 'last3':
            where_conditions.append("DATE >= date('now', '-3 months')")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # Get size distribution
    size_query = f"""
        SELECT 
            COALESCE(SIZE, 'Unspecified') as size,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM mirror_shipments WHERE {where_clause}), 1) as pct,
            ROUND(SUM(CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as single_side_pct,
            ROUND(AVG(UNIT_PRICE_USD), 2) as avg_price,
            GROUP_CONCAT(DISTINCT CONSIGNEE_NAME) as top_buyers
        FROM mirror_shipments
        WHERE {where_clause}
        GROUP BY SIZE
        ORDER BY count DESC
        LIMIT 10
    """
    
    cursor.execute(size_query, params + params)
    sizes = cursor.fetchall()
    
    # Get thickness distribution
    thickness_query = f"""
        SELECT 
            COALESCE(CAST(THICKNESS as TEXT), 'Unspecified') as thickness,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM mirror_shipments WHERE {where_clause}), 1) as pct,
            ROUND(SUM(CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as single_side_pct,
            ROUND(AVG(UNIT_PRICE_USD), 2) as avg_price
        FROM mirror_shipments
        WHERE {where_clause}
        GROUP BY THICKNESS
        ORDER BY count DESC
        LIMIT 10
    """
    
    cursor.execute(thickness_query, params + params)
    thickness_data = cursor.fetchall()
    
    # Get Artis-specific size stats
    artis_query = f"""
        SELECT 
            COUNT(CASE WHEN SIZE IN ('1220x2440', '2440x1220') THEN 1 END) as artis_size_count,
            COUNT(*) as total,
            ROUND(COUNT(CASE WHEN SIZE IN ('1220x2440', '2440x1220') THEN 1 END) * 100.0 / COUNT(*), 1) as artis_pct
        FROM mirror_shipments
        WHERE {where_clause}
    """
    
    cursor.execute(artis_query, params)
    artis_stats = cursor.fetchone()
    
    conn.close()
    
    return {
        "top_size": sizes[0][0] if sizes else 'Unknown',
        "top_size_pct": sizes[0][2] if sizes else 0,
        "artis_size_pct": artis_stats[2] if artis_stats else 0,
        "sizes": [
            {
                "size": row[0],
                "count": row[1],
                "pct": row[2],
                "single_side_pct": row[3] or 0,
                "avg_price": row[4] or 0,
                "top_buyers": (', '.join(row[5].split(',')[:3]) if row[5] else 'Various')[:100] + ('...' if row[5] and len(row[5]) > 100 else '')
            }
            for row in sizes
        ],
        "thickness": [
            {
                "thickness": row[0],
                "count": row[1],
                "pct": row[2],
                "single_side_pct": row[3] or 0,
                "avg_price": row[4] or 0
            }
            for row in thickness_data
        ]
    }

@app.get("/api/competitors")
async def get_competitors(
    countries: List[str] = Query(None),
    product_type: Optional[str] = None,
    min_value: Optional[float] = None,
    size: Optional[str] = None,
    thickness: Optional[str] = None,
    date_range: Optional[str] = None,
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None
):
    """Get competitor analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    if countries:
        placeholders = ','.join(['?' for _ in countries])
        where_conditions.append(f"DESTINATION_COUNTRY IN ({placeholders})")
        params.extend(countries)
    
    if product_type and product_type != 'all':
        where_conditions.append("PRODUCT_TYPE = ?")
        params.append(product_type)
    
    if size and size != 'all':
        if size == '1220x2440':
            where_conditions.append("(SIZE = '2440x1220' OR SIZE = '1220x2440')")
        elif size == 'other':
            where_conditions.append("(SIZE != '2440x1220' AND SIZE != '1220x2440')")
    
    if thickness and thickness != 'all':
        if thickness != 'other':
            where_conditions.append("THICKNESS = ?")
            params.append(float(thickness))
    
    if min_value:
        where_conditions.append("TOTAL_VALUE_USD >= ?")
        params.append(min_value)
    
    # Add date range filter
    if date_range and date_range != 'all':
        if date_range == 'custom' and custom_start and custom_end:
            where_conditions.append(f"DATE BETWEEN '{custom_start}' AND '{custom_end}'")
        elif date_range == '2025':
            where_conditions.append("DATE >= '2025-01-01'")
        elif date_range == '2024':
            where_conditions.append("DATE BETWEEN '2024-01-01' AND '2024-12-31'")
        elif date_range == '2023':
            where_conditions.append("DATE BETWEEN '2023-01-01' AND '2023-12-31'")
        elif date_range == 'recent':
            where_conditions.append("DATE >= date('now', '-12 months')")
        elif date_range == 'last6':
            where_conditions.append("DATE >= date('now', '-6 months')")
        elif date_range == 'last3':
            where_conditions.append("DATE >= date('now', '-3 months')")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # Get top suppliers with country breakdown - market share by VALUE
    query = f"""
        SELECT 
            SHIPPER_NAME,
            ORIGIN_COUNTRY,
            COUNT(*) as orders,
            SUM(TOTAL_VALUE_USD) as total_value,
            ROUND(SUM(TOTAL_VALUE_USD) * 100.0 / (SELECT SUM(TOTAL_VALUE_USD) FROM mirror_shipments WHERE {where_clause}), 1) as value_share,
            SUM(QUANTITY) as total_sheets,
            ROUND(SUM(QUANTITY) * 100.0 / (SELECT SUM(QUANTITY) FROM mirror_shipments WHERE {where_clause}), 1) as volume_share,
            ROUND(SUM(CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as single_side_pct,
            ROUND(AVG(UNIT_PRICE_USD), 2) as avg_price,
            GROUP_CONCAT(DISTINCT CONSIGNEE_NAME) as key_buyers
        FROM mirror_shipments
        WHERE {where_clause}
        GROUP BY SHIPPER_NAME
        ORDER BY total_value DESC
        LIMIT 20
    """
    
    cursor.execute(query, params + params + params)
    competitors = cursor.fetchall()
    
    # Get country breakdown by value for each competitor
    competitor_list = []
    for row in competitors:
        supplier_name = row[0]
        
        # Get top countries by value for this supplier
        country_query = f"""
            SELECT 
                DESTINATION_COUNTRY,
                SUM(TOTAL_VALUE_USD) as country_value
            FROM mirror_shipments
            WHERE SHIPPER_NAME = ? AND ({where_clause})
            GROUP BY DESTINATION_COUNTRY
            ORDER BY country_value DESC
            LIMIT 3
        """
        cursor.execute(country_query, [supplier_name] + params)
        country_data = cursor.fetchall()
        
        # Format top countries with value in millions
        top_countries_str = ', '.join([
            f"{c[0]} (${c[1]/1000000:.1f}M)" for c in country_data
        ])[:120]
        
        competitor_list.append({
            "name": row[0],  # SHIPPER_NAME
            "country": row[1],  # ORIGIN_COUNTRY
            "orders": row[2],  # orders count
            "total_value": row[3],  # total value USD
            "market_share_value": row[4],  # value share %
            "market_share_volume": row[6],  # volume share %
            "single_side_pct": row[7] or 0,  # single side %
            "avg_price": row[8] or 0,  # avg price
            "key_buyers": (', '.join(row[9].split(',')[:3]) if row[9] else 'Various')[:80] + ('...' if row[9] and len(row[9]) > 80 else ''),
            "top_countries": top_countries_str,
            "top_countries_volume": country_data  # Store for volume toggle
        })
    
    conn.close()
    
    return {
        "competitors": competitor_list,
        "supplier_chart": {
            "labels": [row[0][:20] for row in competitors[:10]],
            "values": [row[4] for row in competitors[:10]]  # Use value share, not order count
        }
    }

@app.get("/api/pricing")
async def get_pricing(
    countries: List[str] = Query(None),
    product_type: Optional[str] = None,
    min_value: Optional[float] = None,
    size: Optional[str] = None,
    thickness: Optional[str] = None,
    date_range: Optional[str] = None
):
    """Get pricing analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_conditions = ["UNIT_PRICE_USD > 0 AND UNIT_PRICE_USD < 500"]
    params = []
    
    if countries:
        placeholders = ','.join(['?' for _ in countries])
        where_conditions.append(f"DESTINATION_COUNTRY IN ({placeholders})")
        params.extend(countries)
    
    if product_type and product_type != 'all':
        where_conditions.append("PRODUCT_TYPE = ?")
        params.append(product_type)
    
    if size and size != 'all':
        if size == '1220x2440':
            where_conditions.append("(SIZE = '2440x1220' OR SIZE = '1220x2440')")
        elif size == 'other':
            where_conditions.append("(SIZE != '2440x1220' AND SIZE != '1220x2440')")
    
    if thickness and thickness != 'all':
        if thickness != 'other':
            where_conditions.append("THICKNESS = ?")
            params.append(float(thickness))
    
    if min_value:
        where_conditions.append("TOTAL_VALUE_USD >= ?")
        params.append(min_value)
    
    # Add date range filter
    if date_range and date_range != 'all':
        if date_range == 'custom' and custom_start and custom_end:
            where_conditions.append(f"DATE BETWEEN '{custom_start}' AND '{custom_end}'")
        elif date_range == '2025':
            where_conditions.append("DATE >= '2025-01-01'")
        elif date_range == '2024':
            where_conditions.append("DATE BETWEEN '2024-01-01' AND '2024-12-31'")
        elif date_range == '2023':
            where_conditions.append("DATE BETWEEN '2023-01-01' AND '2023-12-31'")
        elif date_range == 'recent':
            where_conditions.append("DATE >= date('now', '-12 months')")
        elif date_range == 'last6':
            where_conditions.append("DATE >= date('now', '-6 months')")
        elif date_range == 'last3':
            where_conditions.append("DATE >= date('now', '-3 months')")
    
    where_clause = " AND ".join(where_conditions)
    
    # Get average prices
    query = f"""
        SELECT 
            AVG(CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN UNIT_PRICE_USD END) as single_avg,
            AVG(CASE WHEN PRODUCT_TYPE = 'DOUBLE_SIDE' THEN UNIT_PRICE_USD END) as double_avg
        FROM mirror_shipments
        WHERE {where_clause}
    """
    
    cursor.execute(query, params)
    avgs = cursor.fetchone()
    
    # Get price ranges by spec
    spec_query = f"""
        SELECT 
            SIZE || ' - ' || COALESCE(CAST(THICKNESS as TEXT), 'Any') || 'mm' as spec,
            MIN(UNIT_PRICE_USD) as min_price,
            AVG(UNIT_PRICE_USD) as avg_price,
            MAX(UNIT_PRICE_USD) as max_price,
            UNIT_PRICE_USD as mode_price
        FROM mirror_shipments
        WHERE {where_clause} AND SIZE IS NOT NULL
        GROUP BY SIZE, THICKNESS
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """
    
    cursor.execute(spec_query, params)
    price_ranges = cursor.fetchall()
    
    conn.close()
    
    return {
        "single_side_avg": round(avgs[0], 2) if avgs[0] else 0,
        "double_side_avg": round(avgs[1], 2) if avgs[1] else 0,
        "price_ranges": [
            {
                "spec": row[0],
                "min": round(row[1], 2),
                "avg": round(row[2], 2),
                "max": round(row[3], 2),
                "mode": round(row[4], 2)
            }
            for row in price_ranges
        ]
    }

@app.get("/api/insights")
async def get_insights(
    countries: List[str] = Query(None),
    product_type: Optional[str] = None,
    date_range: Optional[str] = None
):
    """Get key insights and recommendations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause for date filtering
    where_conditions = ["UNIT_PRICE_USD > 0 AND UNIT_PRICE_USD < 500"]
    params = []
    
    # Add date range filter
    if date_range and date_range != 'all':
        if date_range == 'custom' and custom_start and custom_end:
            where_conditions.append(f"DATE BETWEEN '{custom_start}' AND '{custom_end}'")
        elif date_range == '2025':
            where_conditions.append("DATE >= '2025-01-01'")
        elif date_range == '2024':
            where_conditions.append("DATE BETWEEN '2024-01-01' AND '2024-12-31'")
        elif date_range == '2023':
            where_conditions.append("DATE BETWEEN '2023-01-01' AND '2023-12-31'")
        elif date_range == 'recent':
            where_conditions.append("DATE >= date('now', '-12 months')")
        elif date_range == 'last6':
            where_conditions.append("DATE >= date('now', '-6 months')")
        elif date_range == 'last3':
            where_conditions.append("DATE >= date('now', '-3 months')")
    
    where_clause = " AND ".join(where_conditions)
    
    # Get market stats for insights
    query = f"""
        SELECT 
            COUNT(CASE WHEN DESTINATION_COUNTRY = 'EGYPT' AND PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 END) as egypt_single,
            COUNT(CASE WHEN DESTINATION_COUNTRY = 'ISRAEL' AND PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 END) as israel_single,
            COUNT(CASE WHEN DESTINATION_COUNTRY = 'UNITED ARAB EMIRATES' AND PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 END) as uae_single,
            COUNT(CASE WHEN DESTINATION_COUNTRY = 'SAUDI ARABIA' AND PRODUCT_TYPE = 'SINGLE_SIDE' THEN 1 END) as saudi_single,
            COUNT(CASE WHEN SIZE IN ('1220x2440', '2440x1220') THEN 1 END) as artis_size_orders,
            AVG(CASE WHEN PRODUCT_TYPE = 'SINGLE_SIDE' THEN UNIT_PRICE_USD END) as single_avg_price
        FROM mirror_shipments
        WHERE {where_clause}
    """
    
    cursor.execute(query, params)
    stats = cursor.fetchone()
    
    conn.close()
    
    opportunities = [
        f"Egypt market: {stats[0]} single-side orders (87.9% preference) - BEST OPPORTUNITY",
        f"Israel market: {stats[1]} single-side orders (78.7% preference) - Strong demand",
        f"UAE market: {stats[2]} single-side orders (58.1% preference) - Largest volume",
        f"Your size (1220x2440) has {stats[3]} orders in the market",
        "AICA LAMINATES orders 428 single-side only - perfect target customer",
        "Average single-side price is ${:.2f} - ensure competitive pricing".format(stats[5] or 0)
    ]
    
    challenges = [
        f"Saudi Arabia only has {stats[3]} single-side orders (9.7% preference)",
        "Top buyer ANMOL INTERNATIONAL prefers double-side (91% of orders)",
        "Many buyers show 'TO ORDER' hiding actual company names",
        "Indian suppliers dominate with 100% market share"
    ]
    
    actions = [
        {"title": "Target Egypt First", "detail": "87.9% single-side preference with buyers like CITY WOOD"},
        {"title": "Focus on UAE Volume", "detail": "4,339 single-side orders, largest market by volume"},
        {"title": "Contact AICA LAMINATES", "detail": "428 orders, 100% single-side, perfect fit"},
        {"title": "Price Competitively", "detail": f"Match market average of ${stats[5]:.2f} for single-side"},
        {"title": "Saudi Strategy", "detail": "Find niche single-side buyers or consider partnerships"}
    ]
    
    summary = f"""
    The GCC laminate market shows strong opportunities for Artis's single-side products, especially in Egypt (87.9% single-side preference) 
    and Israel (78.7%). UAE offers the largest volume with 4,339 single-side orders. Saudi Arabia presents challenges with only 9.7% 
    single-side preference, requiring a targeted approach to specific buyers or partnership strategies. Focus on buyers already purchasing 
    1220x2440mm single-side laminates for quickest market entry.
    """
    
    return {
        "opportunities": opportunities,
        "challenges": challenges,
        "actions": actions,
        "summary": summary
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 GCC INTELLIGENCE DASHBOARD")
    print("="*60)
    print("Multi-tab dashboard with comprehensive filters")
    print("Accurate data from 23,575 import records (includes Jordan, Oman, Bahrain)")
    print("\n📊 Access at: http://localhost:8011")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8011)