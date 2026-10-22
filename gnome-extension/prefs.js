/* exported init */
imports.gi.versions.Gtk = '4.0';
imports.gi.versions.Adw = '1';
const { Adw, Gtk } = imports.gi;

function init() {}

function buildPrefsWidget() {
    const group = new Adw.PreferencesGroup({ title: 'Charging thresholds' });
    const note = new Gtk.Label({
        label: 'Battery Guardian reports controls exposed by your laptop. Thresholds are not supported on every device. This release stores preferences only and does not write to hardware.',
        wrap: true,
        xalign: 0,
        margin_top: 12,
        margin_bottom: 12,
        margin_start: 12,
        margin_end: 12
    });
    group.add(note);

    const desired = new Adw.ActionRow({ title: 'Desired thresholds', subtitle: '50% start · 100% stop' });
    group.add(desired);
    const status = new Gtk.Label({
        label: 'Threshold preferences are not editable in this release. The panel reports whether your battery exposes supported threshold controls. Preset mode names are shown as advertised by the device; Battery Guardian does not assign them behavior or change them.',
        xalign: 0,
        margin: 12,
        wrap: true
    });
    group.add(status);
    return group;
}
