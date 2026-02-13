import React from "react";
import { SafeAreaView, ScrollView, StyleSheet, ViewStyle } from "react-native";

export function ScreenContainer({
  children,
  scroll,
  style
}: {
  children: React.ReactNode;
  scroll?: boolean;
  style?: ViewStyle;
}) {
  if (scroll) {
    return (
      <SafeAreaView style={[styles.container, style]}>
        <ScrollView contentContainerStyle={styles.scrollContent}>{children}</ScrollView>
      </SafeAreaView>
    );
  }

  return <SafeAreaView style={[styles.container, style]}>{children}</SafeAreaView>;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F6F1E8",
    paddingHorizontal: 20,
    paddingTop: 12
  },
  scrollContent: {
    paddingBottom: 40
  }
});
