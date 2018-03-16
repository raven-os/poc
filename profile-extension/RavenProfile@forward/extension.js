const St = imports.gi.St; // library to create UI elements
const Main = imports.ui.main; // Main instance containing UI elements
const Tweener = imports.ui.tweener; // animations of UI elements
const Util = imports.misc.util; // Util used to execute command line
const MessageTray = imports.ui.messageTray; // message tray notification
const Lang = imports.lang; // for object oriented
const PopupMenu = imports.ui.popupMenu; // popupMenu
const PanelMenu = imports.ui.panelMenu; // panelMenu
const Clutter = imports.gi.Clutter; // library to layout UI elements

const Me = imports.misc.extensionUtils.getCurrentExtension(); // this extension
const Gio = imports.gi.Gio; // files?

/* Global variables to use as button to click and text label */
let text, menu;

/* Class PopupMenuProfile derived from PanelMenu.Button 
   It contains the box with icon + label + arrow and menu items */
const PopupMenuProfile = new Lang.Class({
    Name: 'PopupMenuProfile', // Class Name
    Extends: PanelMenu.Button, // Parent class

    // Constructor
    _init: function() {
	/* Parent Constructor
	   First parameter is menu alignment(1=left, 0=right, 0.5=center)
           Second parameter is the name
           Third parameter boolean for automatic menu creation
        */
	this.parent(1, 'PopupMenuProfile', false);

	/* Box that contains elements to add to the top bar :
	    - an icon
            - a label
	    - an arrow
        */
	let box = new St.BoxLayout();

	let gicon = Gio.icon_new_for_string(Me.path + "/raven_profile.svg");
	let icon = new St.Icon({ gicon: gicon,
			         style_class: 'icon'});

	let label = new St.Label({text: ' Profiles ',
	   			  y_expand: true,
				  y_align: Clutter.ActorAlign.CENTER});

	box.add(icon);
	box.add(label);
	box.add(PopupMenu.arrowIcon(St.Side.BOTTOM));

	// Add the box to the button, it will be displayed in the Top Panel
	this.actor.add_child(box);

	let item1 = new PopupMenu.PopupMenuItem('Profile 1');
	let item2 = new PopupMenu.PopupMenuItem('Profile 2');
	this.menu.addMenuItem(item1);
	this.menu.addMenuItem(item2);

        item1.connect('activate', _profile1);
        item2.connect('activate', _profile2);
    },

    // Destructor
    destroy: function() {
	// Call Parent function
	this.parent();
    }
});

function _profile1() {
    _changeProfile("1");
}

function _profile2() {
    _changeProfile("2");
}

/* DEBUG Function to write notification */
function _myNotify(text) {
    global.log("_myNotify called: " + text);

    let source = new MessageTray.SystemNotificationSource();
    Main.messageTray.add(source);
    let notification = new MessageTray.Notification(source, text, null);
    notification.setTransient(true);
    source.notify(notification);
}

/* Function to call when the label is opacity 0%, as the label remains as a 
   UI element, but not visible, we have to delete it explicitily. */
function _hide() {
    Main.uiGroup.remove_actor(text);
    text = null;
}

function _changeProfile(number) {
    Util.spawn([Me.path + '/raven_profile_broadcast.sh', number]);

    /* if text doesn't exists, we create a new UI element using St*/
    text = new St.Label({ style_class: 'helloworld-label',
			      text: "Profile " + number });
    Main.uiGroup.add_actor(text);

    text.opacity = 255;

    /* We choose the monitor to display the label (primaryMonitor) */
    let monitor = Main.layoutManager.primaryMonitor;

    /* change the position of the text to the center of the monitor */
    text.set_position(monitor.x + Math.floor(monitor.width / 2 - text.width / 2),
                      monitor.y + Math.floor(monitor.height / 2 - text.height / 2));

    /* Tweener for animation : go to opacity 0 in 3 secondes and execute _hide */
    Tweener.addTween(text,
                     { opacity: 0,
                       time: 3,
                       transition: 'easeOutQuad',
                       onComplete: _hide });
}

/* This is the init function, here we have to put our code to initialize our extension.
   we have to be careful with init(), enable() and disable() and do the right things here.
*/
function init() {}

/* We have to write here our main extension code and things that actually make the extension works
   (Add UI elements, signals, etc) */
function enable() {
    menu = new PopupMenuProfile;
    Main.panel.addToStatusArea('PopupMenuProfile', menu, 0, 'right');
}

/* We have to delete all connections and things from our extentions,
   to let the system how it was before our extension. */
function disable() {
    menu.destroy();
}
