import 'package:flutter/material.dart';

class AddAppointmentDialog extends StatelessWidget {
  const AddAppointmentDialog({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return const AlertDialog(
      title: Text('Termin hinzufügen'),
    );
  }
}