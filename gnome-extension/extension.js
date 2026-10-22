/* exported init */
const { Gio, GLib, GObject, St } = imports.gi;
const Main = imports.ui.main;
const PanelMenu = imports.ui.panelMenu;
const PopupMenu = imports.ui.popupMenu;
const ExtensionUtils = imports.misc.extensionUtils;

const BUS_NAME = 'org.batteryguardian.Service';
const OBJECT_PATH = '/org/batteryguardian/Service';
const INTERFACE = 'org.batteryguardian.Service';
const XML = `<node><interface name="${INTERFACE}">
  <method name="GetState"><arg type="s" direction="out"/></method>
</interface></node>`;
const Proxy = Gio.DBusProxy.makeProxyWrapper(XML);

const Indicator = GObject.registerClass(
class Indicator extends PanelMenu.Button {
    _init() {
        super._init(0.0, 'Battery Guardian');
        this._label = new St.Label({ text: 'Battery …', y_align: St.Align.MIDDLE });
        this.add_child(this._label);
        this._stateItem = new PopupMenu.PopupMenuItem('Connecting to Battery Guardian…', { reactive: false });
        this.menu.addMenuItem(this._stateItem);
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._infoItem = new PopupMenu.PopupMenuItem('Charging controls are detected from hardware', { reactive: false });
        this.menu.addMenuItem(this._infoItem);
        this._prefsItem = new PopupMenu.PopupMenuItem('Preferences');
        this._prefsItem.connect('activate', () => ExtensionUtils.openPrefs());
        this.menu.addMenuItem(this._prefsItem);
        this._proxy = new Proxy(Gio.DBus.session, BUS_NAME, OBJECT_PATH,
            (proxy, error) => {
                if (error) {
                    this._setUnavailable('Service unavailable. Start battery-guardian.service.');
                    return;
                }
                this._refresh();
                this._timer = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 15, () => {
                    this._refresh();
                    return GLib.SOURCE_CONTINUE;
                });
            });
    }

    _refresh() {
        this._proxy.GetStateRemote((result, error) => {
            if (error) {
                this._setUnavailable('Service unavailable.');
                return;
            }
            try {
                const state = JSON.parse(result[0]);
                this._render(state);
            } catch (parseError) {
                this._setUnavailable('Received invalid service data.');
            }
        });
    }

    _render(state) {
        if (!state.available) {
            this._label.set_text('Battery —');
            this._stateItem.label.set_text('No battery detected');
        } else {
            const pct = state.percentage === null ? '—' : `${state.percentage}%`;
            this._label.set_text(`Battery ${pct}`);
            const ac = state.ac_connected === null ? 'AC status unavailable' : (state.ac_connected ? 'AC connected' : 'On battery power');
            this._stateItem.label.set_text(`${pct} · ${state.status} · ${ac}`);
        }
        const cap = state.capability || {};
        let details = cap.label || 'Monitoring only';
        if (cap.thresholds_supported && cap.thresholds) {
            details += ` (${cap.thresholds.start}%–${cap.thresholds.stop}%)`;
        } else if (cap.modes && cap.modes.length) {
            details += `: ${cap.modes.join(', ')}`;
            if (cap.active_mode)
                details += ` · active: ${cap.active_mode}`;
        }
        if (state.configuration_note)
            details += ` · ${state.configuration_note}`;
        this._infoItem.label.set_text(details);
    }

    _setUnavailable(message) {
        this._label.set_text('Battery Guardian');
        this._stateItem.label.set_text(message);
        this._infoItem.label.set_text('Read-only hardware monitoring');
    }

    destroy() {
        if (this._timer)
            GLib.source_remove(this._timer);
        super.destroy();
    }
});

class Extension {
    constructor() { this._indicator = null; }
    enable() {
        this._indicator = new Indicator();
        Main.panel.addToStatusArea('battery-guardian', this._indicator);
    }
    disable() {
        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }
    }
}

function init() { return new Extension(); }
