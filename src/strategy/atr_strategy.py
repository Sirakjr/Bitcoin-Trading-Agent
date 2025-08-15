from datetime import datetime

class ATRStrategy:
    """
    ATR-based strategy for managing stop-losses and swing trades.
    Uses Average True Range to set dynamic stop-loss levels.
    """
    
    def __init__(self, atr_multiplier=1.5):
        """
        Initialize ATR strategy.
        
        Args:
            atr_multiplier (float): Multiplier for ATR-based stop-loss
        """
        self.atr_multiplier = atr_multiplier
        self.active_trades = []
        self.closed_trades = []
        
        print(f"📊 ATR Strategy initialized:")
        print(f"   ATR Multiplier: {atr_multiplier}")
    
    def calculate_stop_loss(self, entry_price, atr_value, direction="long"):
        """
        Calculate stop-loss price based on ATR.
        
        Args:
            entry_price (float): Entry price of the trade
            atr_value (float): Current ATR value
            direction (str): "long" or "short"
            
        Returns:
            float: Stop-loss price
        """
        atr_stop = atr_value * self.atr_multiplier
        
        if direction == "long":
            # For long positions, stop-loss is below entry
            stop_loss = entry_price - atr_stop
        else:
            # For short positions, stop-loss is above entry
            stop_loss = entry_price + atr_stop
        
        return stop_loss
    
    def open_trade(self, trade_id, entry_price, atr_value, amount_usd, trade_type="swing"):
        """
        Open a new trade with ATR-based stop-loss.
        
        Args:
            trade_id (str): Unique trade identifier
            entry_price (float): Entry price
            atr_value (float): Current ATR value
            amount_usd (float): Trade amount in USD
            trade_type (str): Type of trade (swing, opportunistic, etc.)
            
        Returns:
            dict: Trade details
        """
        stop_loss = self.calculate_stop_loss(entry_price, atr_value, "long")
        
        trade = {
            "trade_id": trade_id,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "amount_usd": amount_usd,
            "btc_amount": amount_usd / entry_price,
            "atr_value": atr_value,
            "trade_type": trade_type,
            "entry_time": datetime.now(),
            "status": "open"
        }
        
        self.active_trades.append(trade)
        
        print(f"📈 Trade opened:")
        print(f"   ID: {trade_id}")
        print(f"   Entry: ${entry_price:,.2f}")
        print(f"   Stop-loss: ${stop_loss:,.2f}")
        print(f"   Amount: ${amount_usd:,.2f}")
        print(f"   ATR: ${atr_value:,.2f}")
        print(f"   Type: {trade_type}")
        
        return trade
    
    def check_stop_loss(self, current_price, trade):
        """
        Check if stop-loss has been hit.
        
        Args:
            current_price (float): Current Bitcoin price
            trade (dict): Trade to check
            
        Returns:
            dict: Stop-loss check result
        """
        if trade["status"] != "open":
            return {"hit": False, "reason": "Trade not open"}
        
        if current_price <= trade["stop_loss"]:
            return {
                "hit": True,
                "reason": f"Stop-loss hit at ${current_price:,.2f}",
                "loss_percent": ((current_price - trade["entry_price"]) / trade["entry_price"]) * 100,
                "loss_usd": (current_price - trade["entry_price"]) * trade["btc_amount"]
            }
        
        return {"hit": False, "reason": "Price above stop-loss"}
    
    def close_trade(self, trade, exit_price, exit_reason="stop_loss"):
        """
        Close a trade and record the result.
        
        Args:
            trade (dict): Trade to close
            exit_price (float): Exit price
            exit_reason (str): Reason for closing
        """
        # Calculate P&L
        pnl_usd = (exit_price - trade["entry_price"]) * trade["btc_amount"]
        pnl_percent = (pnl_usd / trade["amount_usd"]) * 100
        
        # Update trade
        trade["exit_price"] = exit_price
        trade["exit_time"] = datetime.now()
        trade["exit_reason"] = exit_reason
        trade["pnl_usd"] = pnl_usd
        trade["pnl_percent"] = pnl_percent
        trade["status"] = "closed"
        
        # Move to closed trades
        self.active_trades.remove(trade)
        self.closed_trades.append(trade)
        
        print(f"📉 Trade closed:")
        print(f"   ID: {trade['trade_id']}")
        print(f"   Exit: ${exit_price:,.2f}")
        print(f"   P&L: ${pnl_usd:,.2f} ({pnl_percent:+.2f}%)")
        print(f"   Reason: {exit_reason}")
    
    def get_active_trades(self):
        """Get list of active trades."""
        return self.active_trades.copy()
    
    def get_closed_trades(self):
        """Get list of closed trades."""
        return self.closed_trades.copy()
    
    def get_trade_summary(self):
        """Get summary of all trades."""
        if not self.closed_trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "total_pnl": 0,
                "win_rate": 0
            }
        
        total_trades = len(self.closed_trades)
        winning_trades = len([t for t in self.closed_trades if t["pnl_usd"] > 0])
        losing_trades = len([t for t in self.closed_trades if t["pnl_usd"] <= 0])
        total_pnl = sum(t["pnl_usd"] for t in self.closed_trades)
        win_rate = (winning_trades / total_trades) * 100
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "total_pnl": total_pnl,
            "win_rate": win_rate
        }
