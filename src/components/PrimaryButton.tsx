import React from "react";
import { Pressable, Text, StyleSheet, ViewStyle } from "react-native";

export function PrimaryButton({
  title,
  onPress,
  style,
  disabled
}: {
  title: string;
  onPress: () => void;
  style?: ViewStyle;
  disabled?: boolean;
}) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        styles.button,
        disabled && styles.buttonDisabled,
        pressed && !disabled && styles.buttonPressed,
        style
      ]}
    >
      <Text style={styles.text}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: "#1F3A2D",
    paddingVertical: 14,
    paddingHorizontal: 18,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center"
  },
  buttonPressed: {
    opacity: 0.85
  },
  buttonDisabled: {
    backgroundColor: "#9BB3A2"
  },
  text: {
    color: "#F6F1E8",
    fontSize: 16,
    fontWeight: "600"
  }
});
