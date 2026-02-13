import React from "react";
import { StyleSheet, Text, View } from "react-native";

export function StatCard({ title, value, subtitle }: { title: string; value: string; subtitle?: string }) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.value}>{value}</Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderRadius: 16,
    shadowColor: "#1F3A2D",
    shadowOpacity: 0.1,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
    marginBottom: 12
  },
  title: {
    fontSize: 14,
    color: "#5A6A5A",
    fontWeight: "600"
  },
  value: {
    fontSize: 28,
    color: "#1F3A2D",
    fontWeight: "700",
    marginTop: 6
  },
  subtitle: {
    fontSize: 12,
    color: "#8C9B8C",
    marginTop: 4
  }
});
