import 'package:flutter/material.dart';

import '../../../../core/themes/app_colors.dart';
import '../../../../core/themes/theme_controller.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../data/chat_history_repository.dart';
import '../../data/models/chat_history_entry.dart';
import '../widgets/chat_bubble.dart';

class ChatHistoryScreen extends StatefulWidget {
  final ThemeController themeController;
  final ChatHistoryRepository repository;
  final int profileId;

  const ChatHistoryScreen({
    super.key,
    required this.themeController,
    required this.profileId,
    required this.repository,
  });

  @override
  State<ChatHistoryScreen> createState() => _ChatHistoryScreenState();
}

class _ChatHistoryScreenState extends State<ChatHistoryScreen> {
  late final Future<List<ChatHistoryEntry>> _entriesFuture;
  _HistorySortOrder _sortOrder = _HistorySortOrder.descending;

  @override
  void initState() {
    super.initState();
    _entriesFuture = widget.repository.loadEntries(profileId: widget.profileId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CareenaPageHeader(
        title: 'Nachrichten',
        trailing: CareenaThemeHeaderAction(
          onPressed: widget.themeController.toggleTheme,
          isDarkMode: widget.themeController.isDarkMode,
        ),
      ),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 720,
          scrollable: true,
          padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
          child: FutureBuilder<List<ChatHistoryEntry>>(
            future: _entriesFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done) {
                return const Center(child: CircularProgressIndicator());
              }

              final entries = snapshot.data ?? const [];
              if (entries.isEmpty) {
                return const _EmptyChatHistory();
              }

              final sortedEntries = _sortEntries(entries, _sortOrder);
              final groups = _groupEntriesByMonth(sortedEntries);

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Align(
                    alignment: Alignment.centerRight,
                    child: _HistorySortControl(
                      value: _sortOrder,
                      onChanged: (value) {
                        setState(() => _sortOrder = value);
                      },
                    ),
                  ),
                  const SizedBox(height: 12),
                  for (final group in groups) _ChatHistoryGroup(group: group),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

class _HistorySortControl extends StatelessWidget {
  final _HistorySortOrder value;
  final ValueChanged<_HistorySortOrder> onChanged;

  const _HistorySortControl({required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final backgroundColor = isDarkMode
        ? AppColors.segmentedControlBackgroundDark
        : AppColors.lightCard;
    final foregroundColor = isDarkMode
        ? AppColors.darkTextPrimary
        : AppColors.careenaDark;
    final selectedBackgroundColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaSoftAccent;
    final selectedForegroundColor = isDarkMode
        ? AppColors.toolbarButtonForegroundDark
        : AppColors.careenaDark;
    final borderColor = isDarkMode
        ? AppColors.toolbarButtonBackgroundDark
        : AppColors.careenaInfoBorder;

    return SegmentedButton<_HistorySortOrder>(
      segments: const [
        ButtonSegment(
          value: _HistorySortOrder.descending,
          icon: Icon(Icons.south),
          label: Text('Neueste'),
        ),
        ButtonSegment(
          value: _HistorySortOrder.ascending,
          icon: Icon(Icons.north),
          label: Text('Älteste'),
        ),
      ],
      selected: {value},
      showSelectedIcon: false,
      style: SegmentedButton.styleFrom(
        backgroundColor: backgroundColor,
        foregroundColor: foregroundColor,
        selectedBackgroundColor: selectedBackgroundColor,
        selectedForegroundColor: selectedForegroundColor,
        side: BorderSide(color: borderColor, width: 1.5),
      ),
      onSelectionChanged: (selection) {
        onChanged(selection.single);
      },
    );
  }
}

class _ChatHistoryGroup extends StatelessWidget {
  final _HistoryMonthGroup group;

  const _ChatHistoryGroup({required this.group});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: isDarkMode ? AppColors.darkElevatedSurface : AppColors.lightCard,
      elevation: isDarkMode ? 2 : 1,
      shadowColor: isDarkMode
          ? AppColors.darkBackground
          : AppColors.careenaBorder,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: BorderSide(
          color: isDarkMode
              ? Theme.of(
                  context,
                ).colorScheme.outlineVariant.withValues(alpha: 0.35)
              : AppColors.careenaBorder,
        ),
      ),
      child: ExpansionTile(
        initiallyExpanded: true,
        shape: const RoundedRectangleBorder(),
        collapsedShape: const RoundedRectangleBorder(),
        iconColor: isDarkMode
            ? AppColors.toolbarButtonBackgroundDark
            : AppColors.careenaTeal,
        collapsedIconColor: isDarkMode
            ? AppColors.toolbarButtonBackgroundDark
            : AppColors.careenaTeal,
        title: Text(
          group.label,
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        subtitle: Text(_formatEntryCount(group.entries.length)),
        children: [
          for (final entry in group.entries) _ChatHistoryTile(entry: entry),
        ],
      ),
    );
  }
}

class _ChatHistoryTile extends StatelessWidget {
  final ChatHistoryEntry entry;

  const _ChatHistoryTile({required this.entry});

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final colorScheme = Theme.of(context).colorScheme;
    final accentColor = entry.isEmergency
        ? AppColors.warningRed
        : (isDarkMode
              ? AppColors.toolbarButtonBackgroundDark
              : AppColors.careenaTeal);
    final iconBackgroundColor = entry.isEmergency
        ? AppColors.warningIconBackground
        : (isDarkMode
              ? AppColors.toolbarButtonBackgroundDark
              : AppColors.careenaSoftAccent);
    final iconColor = entry.isEmergency
        ? AppColors.warningRed
        : (isDarkMode
              ? AppColors.toolbarButtonForegroundDark
              : AppColors.careenaDark);

    return InkWell(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ChatHistoryDetailScreen(entry: entry),
          ),
        );
      },
      child: Padding(
        padding: const EdgeInsets.fromLTRB(18, 12, 14, 14),
        child: Row(
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: iconBackgroundColor,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                entry.isEmergency
                    ? Icons.warning_amber_rounded
                    : Icons.chat_bubble_outline,
                color: iconColor,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    entry.title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  if (entry.isEmergency) ...[
                    const SizedBox(height: 4),
                    Text(
                      'Notfall',
                      style: TextStyle(
                        color: accentColor,
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                  const SizedBox(height: 4),
                  Text(
                    entry.preview,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: colorScheme.onSurfaceVariant,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  _formatHistoryDate(entry.createdAt),
                  style: TextStyle(
                    color: colorScheme.onSurfaceVariant,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  _formatHistoryTimestamp(entry.createdAt),
                  style: TextStyle(
                    color: colorScheme.onSurfaceVariant,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Icon(Icons.chevron_right, color: colorScheme.onSurfaceVariant),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyChatHistory extends StatelessWidget {
  const _EmptyChatHistory();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.mark_chat_unread_outlined,
            size: 48,
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
          const SizedBox(height: 12),
          const Text(
            'Noch keine gespeicherten Verläufe',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 6),
          Text(
            'Sobald eine Handlungsempfehlung entsteht, erscheint sie hier.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }
}

class ChatHistoryDetailScreen extends StatelessWidget {
  final ChatHistoryEntry entry;

  const ChatHistoryDetailScreen({super.key, required this.entry});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CareenaPageHeader(title: 'Verlauf'),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: 820,
          scrollable: true,
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (final message in entry.messages)
                ChatBubble(message: message, showLongProcessingHint: false),
            ],
          ),
        ),
      ),
    );
  }
}

String _formatHistoryDate(DateTime value) {
  final day = _twoDigits(value.day);
  final month = _twoDigits(value.month);

  return '$day.$month.${value.year}';
}

String _formatHistoryTimestamp(DateTime value) {
  final hour = _twoDigits(value.hour);
  final minute = _twoDigits(value.minute);

  return '$hour:$minute Uhr';
}

String _twoDigits(int value) => value.toString().padLeft(2, '0');

String _formatEntryCount(int count) {
  if (count == 1) {
    return '1 Verlauf';
  }

  return '$count Verläufe';
}

List<ChatHistoryEntry> _sortEntries(
  List<ChatHistoryEntry> entries,
  _HistorySortOrder sortOrder,
) {
  final sortedEntries = List<ChatHistoryEntry>.from(entries)
    ..sort((a, b) => a.createdAt.compareTo(b.createdAt));

  if (sortOrder == _HistorySortOrder.descending) {
    return sortedEntries.reversed.toList();
  }

  return sortedEntries;
}

List<_HistoryMonthGroup> _groupEntriesByMonth(List<ChatHistoryEntry> entries) {
  final groups = <_HistoryMonthGroup>[];

  for (final entry in entries) {
    final year = entry.createdAt.year;
    final month = entry.createdAt.month;
    final existingIndex = groups.indexWhere(
      (group) => group.year == year && group.month == month,
    );

    if (existingIndex == -1) {
      groups.add(
        _HistoryMonthGroup(year: year, month: month, entries: [entry]),
      );
    } else {
      groups[existingIndex].entries.add(entry);
    }
  }

  return groups;
}

enum _HistorySortOrder { descending, ascending }

class _HistoryMonthGroup {
  final int year;
  final int month;
  final List<ChatHistoryEntry> entries;

  _HistoryMonthGroup({
    required this.year,
    required this.month,
    required this.entries,
  });

  String get label => '${_monthLabel(month)} $year';
}

String _monthLabel(int month) {
  return switch (month) {
    1 => 'Januar',
    2 => 'Februar',
    3 => 'März',
    4 => 'April',
    5 => 'Mai',
    6 => 'Juni',
    7 => 'Juli',
    8 => 'August',
    9 => 'September',
    10 => 'Oktober',
    11 => 'November',
    12 => 'Dezember',
    _ => 'Unbekannt',
  };
}
