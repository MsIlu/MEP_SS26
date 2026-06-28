import 'package:flutter/material.dart';
import 'package:app1/core/themes/app_colors.dart';

class AppointmentDialog extends StatelessWidget {
  final String title;

  final TextEditingController doctorController;
  final TextEditingController dateController;
  final TextEditingController timeController;
  final TextEditingController noteController;

  final VoidCallback onPickDate;
  final VoidCallback onPickTime;

  final VoidCallback onSave;
  final VoidCallback? onCancel;
  final String? doctorErrorText;
  final String? dateErrorText;
  final ValueChanged<String>? onDoctorChanged;

  const AppointmentDialog({
    super.key,
    required this.title,
    required this.doctorController,
    required this.dateController,
    required this.timeController,
    required this.noteController,
    required this.onPickDate,
    required this.onPickTime,
    required this.onSave,
    this.onCancel,
    this.doctorErrorText,
    this.dateErrorText,
    this.onDoctorChanged,
  });

  InputDecoration _inputDecoration(String label, IconData icon) {
    return InputDecoration(
      labelText: label,
      labelStyle: const TextStyle(color: AppColors.careenaTeal),
      floatingLabelStyle: const TextStyle(
        color: AppColors.careenaTeal,
        fontWeight: FontWeight.w600,
      ),
      prefixIcon: Icon(icon, color: AppColors.careenaTeal),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: AppColors.careenaTeal, width: 2),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: AppColors.greyShade400),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      title: Text(
        title,
        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
      ),

      content: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 420),
        child: SizedBox(
          width: double.maxFinite,
          child: SingleChildScrollView(
            keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: doctorController,
                  onChanged: onDoctorChanged,
                  decoration: _inputDecoration(
                    'Arzt',
                    Icons.medical_services,
                  ).copyWith(errorText: doctorErrorText),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: dateController,
                  readOnly: true,
                  onTap: onPickDate,
                  decoration: _inputDecoration(
                    'Datum',
                    Icons.calendar_month,
                  ).copyWith(errorText: dateErrorText),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: timeController,
                  readOnly: true,
                  onTap: onPickTime,
                  decoration: _inputDecoration('Uhrzeit', Icons.access_time),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  height: 140,
                  child: TextField(
                    controller: noteController,
                    expands: true,
                    minLines: null,
                    maxLines: null,
                    maxLength: 300,
                    textAlign: TextAlign.start,
                    textAlignVertical: TextAlignVertical.center,
                    keyboardType: TextInputType.multiline,
                    textInputAction: TextInputAction.newline,
                    decoration: _inputDecoration(
                      'Notiz (optional)',
                      Icons.note_alt_outlined,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),

      actions: [
        TextButton(
          style: TextButton.styleFrom(foregroundColor: AppColors.careenaTeal),
          onPressed: onCancel ?? () => Navigator.pop(context),
          child: const Text(
            'Abbrechen',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        FilledButton(
          style: FilledButton.styleFrom(
            backgroundColor: AppColors.careenaTeal,
            foregroundColor: AppColors.white,
          ),
          onPressed: onSave,
          child: const Text('Speichern'),
        ),
      ],
    );
  }
}
