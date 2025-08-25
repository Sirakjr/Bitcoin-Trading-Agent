# Bitcoin Trading Agent - Project Workflow Diagram

## 🔄 **Main Trading Loop Workflow**

```mermaid
graph TD
    A[📱 Scheduler: Every 30 minutes] --> B[🔧 Main Trading Loop]
    B --> C[📊 Fetch Market Data]
    C --> D[💰 Load Configuration]
    D --> E[🧠 Strategy Manager]
    
    E --> F{Portfolio Risk Check}
    F -->|Risk > 25%| G[🚨 Risk Pause - Stop Trading]
    F -->|Risk OK| H[📈 Evaluate DCA Strategy]
    
    H --> I{DCA Should Buy?}
    I -->|Yes| J[💸 Execute DCA Buy]
    I -->|No| K[⏸️ DCA Hold]
    
    E --> L[🔄 Evaluate Swing Trading]
    L --> M{Hybrid Mode Enabled?}
    M -->|Yes| N{ML Forecast Positive?}
    M -->|No| O[🚫 Swing Disabled]
    
    N -->|Yes| P[🎯 Open Swing Position]
    N -->|No| Q[⏸️ Swing Hold]
    
    P --> R[📊 Monitor Active Trades]
    R --> S{Stop Loss Hit?}
    S -->|Yes| T[🛑 Close Swing Position]
    S -->|No| U[📈 Continue Monitoring]
    
    J --> V[💾 Update Portfolio]
    T --> V
    V --> W[📝 Log Trade]
    W --> X[📱 Send Notifications]
    X --> Y[⏰ Wait for Next Cycle]
```

## 🏗️ **System Architecture Components**

```mermaid
graph TB
    subgraph "📱 External Interfaces"
        A1[Telegram Bot]
        A2[Email Reports]
        A3[Google Sheets]
    end
    
    subgraph "🧠 Core Logic"
        B1[Strategy Manager]
        B2[DCA Strategy]
        B3[ML Forecasting]
        B4[Threshold Adapter]
    end
    
    subgraph "💾 Data Layer"
        C1[Price Data API]
        C2[Portfolio Storage]
        C3[Trade History]
        C4[Configuration]
    end
    
    subgraph "🔧 Execution Layer"
        D1[Paper Broker]
        D2[Risk Manager]
        D3[Backtest Engine]
    end
    
    subgraph "⏰ Control Layer"
        E1[Scheduler]
        E2[Main Loop]
        E3[Error Handler]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> B2
    B1 --> B3
    B1 --> B4
    B3 --> B4
    B4 --> B1
    B1 --> D1
    B1 --> D2
    D1 --> C2
    D1 --> C3
    C1 --> B1
    E1 --> E2
    E2 --> B1
    E2 --> D1
```

## 📊 **Data Flow Diagram**

```mermaid
flowchart LR
    A[Coinbase API] --> B[Price Data Module]
    B --> C[ATR Calculation]
    C --> D[Strategy Manager]
    
    E[Environment Config] --> F[Config Manager]
    F --> D
    
    G[ML Forecasting] --> H[Threshold Adapter]
    H --> I[Runtime Overrides]
    I --> D
    
    D --> J[DCA Decision]
    D --> K[Swing Decision]
    
    J --> L[Paper Broker]
    K --> L
    
    L --> M[Portfolio Update]
    L --> N[Trade Log]
    
    M --> O[Risk Check]
    N --> P[Backtest Data]
    
    O --> Q[Telegram/Email]
    P --> R[Performance Analysis]
```

## 🎯 **Strategy Decision Tree**

```mermaid
graph TD
    A[Current Market Data] --> B{Portfolio Risk > 25%?}
    B -->|Yes| C[🚨 PAUSE ALL TRADING]
    B -->|No| D[Continue Trading]
    
    D --> E{DCA Strategy}
    E --> F{Price Drop >= 3%?}
    F -->|Yes| G{Time Interval >= 24h?}
    G -->|Yes| H{Sufficient Budget?}
    H -->|Yes| I[✅ EXECUTE DCA BUY]
    H -->|No| J[❌ Insufficient Funds]
    G -->|No| K[⏰ Wait for Time]
    F -->|No| L[📈 Price Too High]
    
    D --> M{Swing Trading}
    M --> N{Hybrid Mode Enabled?}
    N -->|No| O[🚫 Swing Disabled]
    N -->|Yes| P{ML Forecast > 0?}
    P -->|Yes| Q{ATR Available?}
    Q -->|Yes| R[✅ OPEN SWING POSITION]
    Q -->|No| S[❌ No ATR Data]
    P -->|No| T[📉 Bearish Forecast]
    
    R --> U[Monitor Stop Loss]
    U --> V{Price <= Stop Loss?}
    V -->|Yes| W[🛑 CLOSE SWING POSITION]
    V -->|No| X[📊 Continue Monitoring]
```

## 🔄 **Backtesting Workflow**

```mermaid
graph TD
    A[Historical Data] --> B[Backtest Engine]
    B --> C[Initialize Strategy Manager]
    C --> D[Load Configuration]
    D --> E[Process Each Bar]
    
    E --> F[Calculate ATR]
    F --> G[Evaluate Strategy]
    G --> H{Execute Trades?}
    
    H -->|Yes| I[Update Portfolio]
    H -->|No| J[Record Portfolio State]
    
    I --> K[Log Trade]
    K --> L[Update Portfolio State]
    L --> M{More Data?}
    
    J --> M
    M -->|Yes| E
    M -->|No| N[Calculate Results]
    
    N --> O[Save Results]
    O --> P[Generate Report]
```

## 📱 **Notification System**

```mermaid
graph LR
    A[Trading Event] --> B{Event Type}
    
    B -->|DCA Buy| C[Telegram Bot]
    B -->|Swing Open| C
    B -->|Stop Loss| C
    B -->|Risk Alert| C
    
    B -->|Daily Report| D[Email Report]
    B -->|Weekly Summary| D
    
    B -->|Portfolio Update| E[Google Sheets]
    B -->|Trade Log| E
    
    C --> F[User Notification]
    D --> G[Email Inbox]
    E --> H[Spreadsheet]
```

## 🔧 **Configuration Management**

```mermaid
graph TD
    A[Environment Variables] --> B[Config Manager]
    C[.env File] --> B
    D[Runtime Overrides] --> B
    
    B --> E[Trading Parameters]
    B --> F[Risk Settings]
    B --> G[Notification Settings]
    B --> H[Data Source Settings]
    
    E --> I[Strategy Manager]
    F --> I
    G --> J[Notification Modules]
    H --> K[Data Modules]
```

## 📊 **Key Metrics & Monitoring**

```mermaid
graph LR
    A[Portfolio Value] --> B[Drawdown Calculation]
    B --> C[Risk Management]
    
    D[Trade History] --> E[Performance Metrics]
    E --> F[Return Analysis]
    
    G[ATR Values] --> H[Volatility Monitoring]
    H --> I[Stop Loss Adjustment]
    
    J[ML Forecasts] --> K[Strategy Adaptation]
    K --> L[Parameter Tuning]
```

## 🚀 **Deployment & Execution**

```mermaid
graph TD
    A[Docker Build] --> B[Container Image]
    B --> C[Docker Compose]
    C --> D[Service Startup]
    
    D --> E[Scheduler Service]
    D --> F[Main Trading Service]
    
    E --> G[30-min Intervals]
    F --> H[Trading Execution]
    
    H --> I[Log Generation]
    H --> J[Data Persistence]
    
    I --> K[Monitoring Dashboard]
    J --> L[Backup & Recovery]
```

---

## 📋 **Component Summary**

### **Core Trading Engine**
- **Strategy Manager**: Orchestrates DCA and swing trading decisions
- **DCA Strategy**: Dollar-cost averaging logic with configurable triggers
- **ML Forecasting**: ARIMA(1,1,2) model for price prediction
- **Threshold Adapter**: ML-driven parameter adjustment

### **Risk Management**
- **Portfolio Risk Check**: 25% drawdown protection
- **ATR-based Stops**: Dynamic stop-loss calculation
- **Position Sizing**: Configurable trade amounts

### **Data & Execution**
- **Price Data**: Coinbase API integration with ATR calculation
- **Paper Broker**: Simulated trading execution
- **Portfolio Tracking**: JSON-based state management

### **Monitoring & Notifications**
- **Telegram Bot**: Real-time trading alerts
- **Email Reports**: Daily/weekly summaries
- **Google Sheets**: Portfolio tracking

### **Testing & Validation**
- **Backtest Engine**: Historical strategy validation
- **Configuration Management**: Environment-based settings
- **Error Handling**: Graceful failure management

This workflow shows how the Bitcoin Trading Agent operates as a complete, automated system that continuously monitors the market, makes intelligent trading decisions, and manages risk while providing comprehensive monitoring and reporting capabilities.
