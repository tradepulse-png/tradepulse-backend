import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  Alert,
} from "react-native";

// ⭐ CHANGE THIS TO YOUR PC LAN IP ⭐
const API_BASE = "http://192.168.0.104";

// -------------------------------
// Types
// -------------------------------
type StatusResponse = {
  autotrade_enabled: boolean;
  balance: number;
  unrealizedPL: number;
  openTradeCount: number;
  last_action: string | null;
  history_count: number;
};

// -------------------------------
// Screen Component
// -------------------------------
export default function TradingScreen() {
  const [loadingBtn, setLoadingBtn] = useState<string | null>(null);

  // -------------------------------
  // Commands to Backend
  // -------------------------------
  const sendCommand = async (type: "buy" | "sell" | "close") => {
    try {
      setLoadingBtn(type.toUpperCase());

      const res = await fetch(`${API_BASE}/${type}`, {
        method: "POST",
      });

      const json = await res.json();
      console.log(json);

      Alert.alert("TradePulse Bot", `${type.toUpperCase()} executed!`);
    } catch (err) {
      console.log(err);
      Alert.alert("Error", "Could not reach backend.");
    } finally {
      setLoadingBtn(null);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>TradePulse Bot</Text>

      {/* ------------ BUY BUTTON ------------ */}
      <TouchableOpacity
        style={styles.btn}
        onPress={() => sendCommand("buy")}
        disabled={loadingBtn !== null}
      >
        {loadingBtn === "BUY" ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>BUY</Text>
        )}
      </TouchableOpacity>

      {/* ------------ SELL BUTTON ------------ */}
      <TouchableOpacity
        style={styles.btn}
        onPress={() => sendCommand("sell")}
        disabled={loadingBtn !== null}
      >
        {loadingBtn === "SELL" ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>SELL</Text>
        )}
      </TouchableOpacity>

      {/* ------------ CLOSE BUTTON ------------ */}
      <TouchableOpacity
        style={[styles.btn, styles.closeBtn]}
        onPress={() => sendCommand("close")}
        disabled={loadingBtn !== null}
      >
        {loadingBtn === "CLOSE" ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>CLOSE</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

// -------------------------------
// Styles
// -------------------------------
const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: "#000",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 40,
  },
  title: {
    fontSize: 30,
    fontWeight: "bold",
    color: "#fff",
    marginBottom: 40,
  },
  btn: {
    width: "70%",
    backgroundColor: "#0ab4ff",
    paddingVertical: 18,
    borderRadius: 10,
    marginVertical: 10,
    alignItems: "center",
  },
  closeBtn: {
    backgroundColor: "#ff4444",
  },
  btnText: {
    fontSize: 20,
    color: "#fff",
    fontWeight: "bold",
  },
});
