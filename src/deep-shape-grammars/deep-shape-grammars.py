#!/usr/bin/env python3

#   Deep-Shape-Grammars - Shape grammars with deep learning
#   Copyright (C) 2022 AILab FOI <markus.schatten@foi.hr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi
import os
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
from gi.repository import Gimp
from gi.repository import GimpUi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gio
from gi.repository import GLib

import tempfile


import sys
import shapegrammar as sg
from match_template import generate_similar_bboxes_matching_template

import gettext
_ = gettext.gettext
def N_(message): return message

PROC_NAME = 'python-fu-deep-shape-grammars'

RESPONSE_BROWSE, RESPONSE_CLEAR, RESPONSE_NEW = range(3)

def run(procedure, run_mode, image, n_drawables, drawables, args, data):
    GimpUi.init ("deep-shape-grammars.py")

    

    class DSGDialog(GimpUi.Dialog):
        def __init__(self):
            use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")
            GimpUi.Dialog.__init__(self, use_header_bar=use_header_bar)
            self.set_property("help-id", PROC_NAME)
            Gtk.Window.set_title(self, _("Deep Shape Grammars"))
            Gtk.Window.set_role(self, PROC_NAME)
            Gtk.Dialog.add_button(self, "_New grammar", Gtk.ResponseType.OK)
            Gtk.Dialog.add_button(self, "Cl_ear", RESPONSE_CLEAR)
            Gtk.Dialog.add_button(self, _("_Browse existing grammars..."), RESPONSE_BROWSE)
            Gtk.Dialog.add_button(self, "_Close", Gtk.ResponseType.CLOSE)

            Gtk.Widget.set_name (self, PROC_NAME)
            GimpUi.Dialog.set_alternative_button_order_from_array(self,
                                                                [ Gtk.ResponseType.CLOSE,
                                                                  RESPONSE_BROWSE,
                                                                  RESPONSE_CLEAR,
                                                                  Gtk.ResponseType.OK ])

            self.style_set (None, None)

            self.connect('response', self.response)
            self.connect('style-set', self.style_set)

            self.browse_dlg = None
            self.save_dlg = None

           
        def style_set(self, old_style, user_data):
            pass
            #style = Gtk.Widget.get_style (self)
            #self.cons.stdout_tag.set_property ("foreground", style.text[Gtk.StateType.NORMAL])
            #self.cons.stderr_tag.set_property ("foreground", style.text[Gtk.StateType.INSENSITIVE])

        def response(self, dialog, response_id):
            if response_id == RESPONSE_BROWSE:
                self.browse()
            elif response_id == RESPONSE_CLEAR:
                self.clear()
            elif response_id == Gtk.ResponseType.OK:
                self.new_grammar()
            else:
                Gtk.main_quit()


        def browse( self ):
            print( 'Browsing grammars' )

        def clear( self ):
            print( 'Clearing current grammar' )

        def new_grammar( self ):
            print( 'Creating new grammar' )
            #image = GObject.Value( Gimp.Image, image )
            layer = image.get_active_layer()
            sel = image.get_selection()
            #pixels = sel.get_data()

            #get_pixel_rgn(0, 0, image.width, image.height)

            #print( pixels )

            print( image )
            print( sel )

            print( dir( sel ) )

            print( sel.bounds( image ) )

            def get_image():
                im = Gimp.get_pdb().run_procedure( 'gimp-get-images', [ ] )
                image = im.index( 2 ).data[ 0 ]

                return image

            def save_image(img, layer, path):
                return Gimp.get_pdb().run_procedure( 'file-png-save', [
                    GObject.Value( Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE ),
                    GObject.Value( Gimp.Image, img ),
                    GObject.Value( GObject.TYPE_INT, 1 ),
                    GObject.Value( Gimp.ObjectArray, Gimp.ObjectArray.new( Gimp.Drawable, [ layer ], False ) ),
                    GObject.Value( Gio.File, Gio.File.new_for_path( path ) ),
                    GObject.Value( GObject.TYPE_BOOLEAN, 0 ),
                    GObject.Value( GObject.TYPE_INT, 2 ),
                    GObject.Value( GObject.TYPE_BOOLEAN, True ),
                    GObject.Value( GObject.TYPE_BOOLEAN, False ),
                    GObject.Value( GObject.TYPE_BOOLEAN, True ),
                    GObject.Value( GObject.TYPE_BOOLEAN, True ),
                    GObject.Value( GObject.TYPE_BOOLEAN, True ),
                ])

            def get_image_selection_bounds(img):
                bounds = Gimp.get_pdb().run_procedure( 'gimp-selection-bounds', [
                    GObject.Value( Gimp.Image, img )
                ])
                
                return bounds.index(1), bounds.index(2), bounds.index(3), bounds.index(4), bounds.index(5)

            def corp_image(img, x1, y1, x2, y2):
                Gimp.get_pdb().run_procedure( 'gimp-image-crop', [
                    GObject.Value( Gimp.Image, img ),
                    x2 - x1,
                    y2 - y1,
                    x1,
                    y1
                ])

            path = os.path.dirname( sys.argv[0] )
            active_image = get_image()

            # save org image
            org_img = active_image.duplicate()
            org_layer = org_img.merge_visible_layers( Gimp.MergeType.CLIP_TO_IMAGE )
            org_img_path = f'{path}/image.png'
            save_image(org_img, org_layer, org_img_path )

            # save selection image
            selection_img = active_image.duplicate()
            selection_exists, x1, y1, x2, y2 = get_image_selection_bounds(selection_img)
            corp_image( selection_img, x1, y1, x2, y2 )
            selection_layer = selection_img.merge_visible_layers( Gimp.MergeType.CLIP_TO_IMAGE )
            selection_img_path = f'{path}/selection.png'
            save_image( selection_img, selection_layer, selection_img_path )

            bboxes = generate_similar_bboxes_matching_template( org_img_path, selection_img_path, False )
            print( bboxes )


            #result = Gimp.get_pdb().run_procedure('file-png-save', [
            #    GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
            #    GObject.Value( Gimp.Image, image ),
            #    GObject.Value(  ),
            #    GObject.Value(Gio.File, next(tempfile._get_candidate_names())),
            #])

            '''
            (file-png-save TRUE
			       img
			       (aref (cadr (gimp-image-get-layers img)) 0)
			       new-name
			       new-name
			       TRUE 9 FALSE TRUE FALSE FALSE TRUE)
            '''


            
            temp_name = next(tempfile._get_candidate_names())
            
            sg.new_grammar()

    DSGDialog().run()

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

class DeepShapeGrammar( Gimp.PlugIn ):
    ## Properties: parameters ##
    @GObject.Property(type=Gimp.RunMode,
                      default=Gimp.RunMode.NONINTERACTIVE,
                      nick="Run mode", blurb="The run mode")
    def run_mode(self):
        """Read-write integer property."""
        return self.runmode

    @run_mode.setter
    def run_mode(self, runmode):
        self.runmode = runmode

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        # Localization
        self.set_translation_domain ("gimp30-python",
                                     Gio.file_new_for_path(Gimp.locale_directory()))

        return [ PROC_NAME ]

    def do_create_procedure(self, name):
        if name == PROC_NAME:
            procedure = Gimp.ImageProcedure.new(self, name,
                                           Gimp.PDBProcType.PLUGIN,
                                           run, None)
            procedure.set_menu_label(N_("_Deep Shape Grammars"))
            procedure.set_documentation(N_("Shape grammars based on deep-learning"),
                                        "Create rules and execute the on the current",
                                        "image")
            procedure.set_attribution("AILab FOI",
                                      "AILab FOI",
                                      "2022")
            procedure.add_argument_from_property(self, "run-mode")
            procedure.add_menu_path ("<Image>/Filters/Artistic")

            return procedure
        return None

Gimp.main( DeepShapeGrammar.__gtype__, sys.argv )
