import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:flutter/material.dart';

import '../controllers/medication_plan_controller.dart';
import '../widgets/form/medication_form_dialog.dart';
import '../widgets/list/medication_list_dialog.dart';
import '../widgets/layout/medication_plan_content.dart';

/// Page for managing personal medications and daily intake reminders.
class MedicationPlanPage extends StatefulWidget {
  final ThemeController themeController;

  const MedicationPlanPage({super.key, required this.themeController});

  @override
  State<MedicationPlanPage> createState() => _MedicationPlanPageState();
}

class _MedicationPlanPageState extends State<MedicationPlanPage> {
  final _controller = MedicationPlanController();

  late final DateTime _today;
  late DateTime _selectedDate;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _today = DateTime(now.year, now.month, now.day);
    _selectedDate = _today;
    _controller.loadEntries();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final horizontalPadding = MediaQuery.sizeOf(context).width < 360
        ? 16.0
        : 20.0;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, _) {
            return ResponsivePageBody(
              maxWidth: 720,
              scrollable: false,
              padding: EdgeInsets.fromLTRB(
                horizontalPadding,
                18,
                horizontalPadding,
                14,
              ),
              child: MedicationPlanContent(
                themeController: widget.themeController,
                selectedDate: _selectedDate,
                today: _today,
                entries: _controller.entries,
                onDateSelected: (date) {
                  setState(() => _selectedDate = date);
                },
                onOpenMedicationList: _openMedicationList,
                onAddMedication: _openMedicationForm,
                onTakenChanged: _controller.toggleTakenForDate,
              ),
            );
          },
        ),
      ),
    );
  }

  /// Opens a centered form dialog and prepares clean input state first.
  Future<void> _openMedicationForm() async {
    final wasSaved = await showDialog<bool>(
      context: context,
      builder: (context) {
        return MedicationFormDialog(
          onSave:
              (
                name,
                dose,
                intakeTime,
                secondIntakeTime,
                frequency,
                remindersEnabled,
                catalogItem,
              ) {
                return _controller.addEntry(
                  name: name,
                  dose: dose,
                  intakeTime: intakeTime,
                  secondIntakeTime: secondIntakeTime,
                  frequency: frequency,
                  remindersEnabled: remindersEnabled,
                  catalogItem: catalogItem,
                );
              },
        );
      },
    );

    if (mounted && wasSaved == true) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Medikament gespeichert')));
    }
  }

  /// Opens the saved medication list without leaving the current day context.
  Future<void> _openMedicationList() async {
    await showDialog<void>(
      context: context,
      builder: (context) {
        return Dialog(
          insetPadding: const EdgeInsets.all(18),
          backgroundColor: Colors.transparent,
          child: ResponsiveFrame(
            maxWidth: 720,
            child: Container(
              constraints: const BoxConstraints(maxHeight: 620),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                borderRadius: BorderRadius.circular(20),
              ),
              child: AnimatedBuilder(
                animation: _controller,
                builder: (context, _) {
                  return MedicationListDialog(
                    isLoading: _controller.isLoading,
                    entries: _controller.entries,
                    onAdd: () => _openMedicationFormFromList(context),
                    onClose: () => Navigator.pop(context),
                    onToggleReminder: _controller.toggleReminder,
                    onDelete: _controller.deleteEntry,
                  );
                },
              ),
            ),
          ),
        );
      },
    );
  }

  /// Closes the list dialog before opening the add form to avoid stacked modals.
  Future<void> _openMedicationFormFromList(BuildContext sheetContext) async {
    Navigator.pop(sheetContext);
    await Future<void>.delayed(const Duration(milliseconds: 160));

    if (mounted) {
      await _openMedicationForm();
    }
  }
}
