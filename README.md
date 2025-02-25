# Global Value Chain (GVC) and Carbon Emissions Analysis

## 📌 Final Project Write-Up
### 👥 Group Members
- **Joy Wu**: Data Cleaning & Altair Plots ([GitHub: XiaoXiguaZI](https://github.com/XiaoXiguaZI))
- **Betsy Shi**: Shiny App Development ([GitHub: BetsyShi00](https://github.com/BetsyShi00))

## 🎯 Research Question
Our research explores the relationship between **Global Value Chain (GVC) participation** and **carbon dioxide (CO2) emissions**. We analyze how GVC patterns influence emissions at both **country** and **industry** levels, providing insights for **global sustainability** and **policy recommendations** on emission reduction.

## 🏗️ Approach and Methodology
### 🔢 Key Metrics
We developed five GVC metrics from **Wang et al. (2017)**:
- **Forward Linkage**
- **Backward Linkage**
- **GVC Participation**
- **GVCS (GVC Structure)**
- **GVCC (GVC Complexity)**

These metrics **decompose GDP at the country-sector level**, emphasizing intermediate goods flows. **CO2 emissions (CE)** serve as our key environmental impact metric.

### 📊 Datasets
We merged **GVC participation data** and **CO2 emissions data**, covering **42 countries and 56 industries (2000–2014)**. The dataset was cleaned by:
- Merging GVC metrics with CE using **country, year, and industry** as keys.
- Addressing **missing values** and **standardizing industry codes**.
- Creating **static and interactive visualizations** for analysis.

## 📈 Data Analysis and Visualization
### 📌 Static Plots
- **Figure 1: GVC Participation Trends** – Tracks major economies (US, China, Japan, Russia) from **2001–2015**. Global GVC participation **rose until 2011** but **plateaued post-2012**.
- **Figure 2: Global GVC Participation (Geospatial)** – Highlights developed economies (e.g., **Western Europe**) as **hubs for high-value production**.
- **Figure 3: Sectoral Participation** – Categorizes industries into **agriculture, mining, manufacturing, and services**. Manufacturing exhibits **balanced, high participation**, while agriculture remains **low**.
- **Figure 4: Country-Specific Trends** – Shows **GVC metrics vs. CO2 emissions**. **China leads** in both metrics and emissions, positioning itself as a **global manufacturing hub**.

### 🌍 Shiny App Exploration
We built an **interactive Shiny dashboard** to provide **dynamic insights**:
- **📌 Page 1: Global Overview** – Geo-maps and tables display **CO2 emissions concentration** in industrialized nations (e.g., USA, China).
- **📌 Page 2: Nation-Level Analysis** – Scatter plots reveal that **developed countries manage carbon growth better** despite high GVC participation.
- **📌 Page 3: Industry-Level Analysis** – Industry-specific scatter plots highlight **manufacturing variability**, reflecting **efficiency differences**.

## 🌍 Policy Implications
Promoting **sustainable GVCs** requires:
- **♻️ Low-Carbon GVCs**: Incentivizing **clean technologies** & efficient processes.
- **📜 Industry Standards**: Tailoring policies for **high-emission sectors** like manufacturing.
- **🤝 Global Collaboration**: Strengthening **carbon accountability agreements** across supply chains.

## 🚀 Future Work
- **Granular regional data analysis**.
- **Dynamic modeling under policy scenarios**.
- **Post-COVID supply chain shifts & longitudinal studies**.

---
### 📥 [View on GitHub](https://github.com/XiaoXiguaZI) | 📄 [Download Full Report](resume.pdf)
