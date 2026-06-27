import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

class AppTheme {
  AppTheme._();

  static ThemeData lightTheme = ThemeData(
    fontFamily: 'Nunito',
    brightness: Brightness.light,
    scaffoldBackgroundColor: AppColors.lightBackground,
    primaryColor: AppColors.primary,
    colorScheme: const ColorScheme.light(
      primary: AppColors.primary,
      secondary: AppColors.accent,
      surface: AppColors.lightCard,
      onSurface: AppColors.lightTextPrimary,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.upperBarColor,
      foregroundColor: AppColors.white,
      elevation: 0,
    ),
    cardTheme: const CardThemeData(
      color: AppColors.lightCard,
    ),
    textTheme: const TextTheme(
      bodyMedium: TextStyle(color: AppColors.lightTextPrimary),
      bodySmall: TextStyle(color: AppColors.lightTextSecondary),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.lightCard,
      labelStyle: const TextStyle(color: AppColors.lightTextPrimary),
      floatingLabelStyle: const TextStyle(
        color: AppColors.lightTextPrimary,
        fontWeight: FontWeight.w600,
      ),
      hintStyle: const TextStyle(color: AppColors.lightTextPrimary),
      prefixIconColor: AppColors.lightTextPrimary,
      suffixIconColor: AppColors.lightTextPrimary,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: AppColors.greyShade400),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: AppColors.greyShade400),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: AppColors.greyShade400, width: 2),
      ),
    ),
  );

  static ThemeData darkTheme = ThemeData(
    fontFamily: 'Nunito',
    brightness: Brightness.dark,
    scaffoldBackgroundColor: AppColors.darkBackground,
    primaryColor: AppColors.primary,
    colorScheme: const ColorScheme.dark(
      primary: AppColors.primary,
      secondary: AppColors.accent,
      surface: AppColors.darkCard,
      onSurface: AppColors.darkTextPrimary,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.darkCard,
      foregroundColor: AppColors.darkTextPrimary,
      elevation: 0,
    ),
    cardTheme: const CardThemeData(
      color: AppColors.darkCard,
    ),
    textTheme: const TextTheme(
      bodyMedium: TextStyle(color: AppColors.darkTextPrimary),
      bodySmall: TextStyle(color: AppColors.darkTextSecondary),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.darkCard,
      labelStyle: const TextStyle(color: AppColors.darkTextPrimary),
      floatingLabelStyle: const TextStyle(
        color: AppColors.darkTextPrimary,
        fontWeight: FontWeight.w600,
      ),
      hintStyle: const TextStyle(color: AppColors.darkTextPrimary),
      prefixIconColor: AppColors.darkTextPrimary,
      suffixIconColor: AppColors.darkTextPrimary,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: AppColors.greyShade400),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: AppColors.greyShade400),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: AppColors.greyShade400, width: 2),
      ),
    ),
  );
}
