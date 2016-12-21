#!/usr/bin/env python3
#
# mainwindow.py - Main window of the tarsierstock application.
#
# Copyright (c) 2015 - Jesus Vedasto Olazo <jessie@jestoy.frihost.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import os, csv, sqlite3

from createdatabase import *
from itemmaster import *
from companydetails import *
from itemin import *
from itemout import *


__appname__ = "Tarsier Stock"
__description__ = "A simple inventory software for small business."
__version__ = "0.2"
__author__ = "Jesus Vedasto Olazo"
__email__ = "jestoy.olazo@gmail.com"
__web__ = "http://jestoy.frihost.net"
__license__ = "GPLV2"
__status__ = "Development"
__maintainer__ = "Jesus Vedasto Olazo"
__copyright__ = "Copyright (c) 2015 - Jesus Vedasto Olazo"


class Reports(tk.Toplevel):

    def __init__(self, master):
        """
        Initialize the graphics user interface for stock reporting.
        """
        tk.Toplevel.__init__(self, master)
        self.title('Stock Report')
        self.protocol('WM_DELETE_WINDOW', self.quitApp)
        container = tk.Frame(self)
        container.pack(fill='both', expand=True)

        # Set the window icon.
        self.iconlocation = os.getcwd() + "/tsicon.ico"
        try:
            self.iconbitmap(self.iconlocation)
        except:
            pass

        # Initialize the database.
        self.database = sqlite3.connect('inv_database.db')
        self.cur = self.database.cursor()

        # Create a label for the window.
        report_label = ttk.Label(container, text='Stock Report')
        report_label.pack(padx=7, pady=7)
        report_label.config(font=('Helvetica', 15, 'bold'))

        # Create container for the treeview and scrollbar.
        display_frame = tk.Frame(container)
        display_frame.pack(expand=True, fill='both')

        # Create a tkinter.ttk treeview.
        self.display_tree = ttk.Treeview(display_frame)
        self.display_tree.pack(side='left', expand=True, fill='both')

        # Create a scrollbar for the treeview.
        yscrollbar = tk.Scrollbar(display_frame)
        yscrollbar.pack(side='left', fill='y')
        yscrollbar.config(command=self.display_tree.yview)
        self.display_tree.config(yscrollcommand=yscrollbar.set)

        # Initialize column and heading variable.
        self.headers = ('Item Code',
                        'Description',
                        'Unit',
                        'In',
                        'Out',
                        'Balance'
                        )
        
        self.column = ('itemcode',
                       'description',
                       'unit',
                       'incoming',
                       'outgoing',
                       'balance'
                       )

        # Set the column of the tree.
        self.display_tree['columns'] = self.column

        # Set the heading of the tree and the width of each column.
        counter = 0
        self.display_tree.heading('#0', text='S. No.')
        self.display_tree.column('#0', width=40)
        for head in self.column:
            if head == 'itemcode':
                setwidth = 85
            elif head == 'description':
                setwidth = 180
            else:
                setwidth = 50
            self.display_tree.heading(head, text=self.headers[counter])
            self.display_tree.column(head, width=setwidth)
            counter += 1
        # Create tags for treeview.
        self.display_tree.tag_configure('evenrow', background='#FFB586')
        self.display_tree.tag_configure('oddrow', background='#FDA46A')

        # Insert the details to the tree.
        self.insertDetails()

        # Create a button below the treeview for exporting
        # the report to a csv file.
        self.export_btn = ttk.Button(self, text='Export',
                                     command=self.exportFile
                                     )
        self.export_btn.pack()

    def insertDetails(self):
        """
        This method is for inserting all the details from the database
        to the treeview so that it can be shown to the user the total
        incoming and outgoing items and the balance for each items in the
        item master listing.
        """
        # Combine incoming and outgoing material
        item_table = self.cur.execute("SELECT * FROM item")
        item_table_fetch = item_table.fetchall()
        in_table = self.cur.execute("SELECT itemcode, quantity FROM incoming")
        in_table_fetch = in_table.fetchall()
        out_table = self.cur.execute("SELECT itemcode, quantity FROM outgoing")
        out_table_fetch = out_table.fetchall()

        counter = 1
        for elem in item_table_fetch:
            if counter % 2 == 0:
                self.display_tree.insert('', 'end', str(elem[0]), text=str(elem[0]), tag=('evenrow',))
            else:
                self.display_tree.insert('', 'end', str(elem[0]), text=str(elem[0]), tag=('oddrow',))
            self.display_tree.set(str(elem[0]), self.column[0], str(elem[1]))
            self.display_tree.set(str(elem[0]), self.column[1], str(elem[2]))
            self.display_tree.set(str(elem[0]), self.column[2], str(elem[3]))
            itotal = 0
            for inqty in in_table_fetch:
                if inqty[0] == elem[1]:
                    itotal += inqty[1]
            self.display_tree.set(str(elem[0]), self.column[3], str(itotal))
            ototal = 0
            for outqty in out_table_fetch:
                if outqty[0] == elem[1]:
                    ototal += outqty[1]
            self.display_tree.set(str(elem[0]), self.column[4], str(ototal))
            self.display_tree.set(str(elem[0]), self.column[5], str(itotal + ototal))
            counter += 1

    def exportFile(self):
        """
        This method is for exporting the stock report into a csv file
        for further editing due to lack of printing support from tkinter
        module. From the csv file they can manipulate easily the details
        so that it can be print into the printer with ease and report can
        be easily forwarded via e-mail.
        """
        # Initialize the data to be shown
        item_table = self.cur.execute("SELECT * FROM item")
        item_table_fetch = item_table.fetchall()
        in_table = self.cur.execute("SELECT itemcode, quantity FROM incoming")
        in_table_fetch = in_table.fetchall()
        out_table = self.cur.execute("SELECT itemcode, quantity FROM outgoing")
        out_table_fetch = out_table.fetchall()

        # Start saving it into a csv file.
        with open('exportfile.csv', 'w', newline='') as csvfile:
            cwriter = csv.writer(csvfile, delimiter=',',
                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # Write the title of the report.
            cwriter.writerow(['Stock Report - Al Hamra Maintenance'])
            # Then write the header of the report.
            cwriter.writerow(['S. No.',
                              'Item Code',
                              'Description',
                              'Unit',
                              'In',
                              'Out',
                              'Balance'
                              ])
            # Start writing the details into the csv file.
            for row in item_table_fetch:
                
                # Check the itemcode if there is any in transaction.
                # if so, sum the quantity of that transaction.
                itotal = 0
                for inqty in in_table_fetch:
                    if inqty[0] == row[1]:
                        itotal += inqty[1]

                ototal = 0
                
                # Check the itemcode if there is any out transaction.
                # if so, sum the quantity of that transaction.
                for outqty in out_table_fetch:
                    if outqty[0] == row[1]:
                        ototal += outqty[1]
                # Start writing the details in the csv file.  
                cwriter.writerow([row[0],
                                  row[1],
                                  row[2],
                                  row[3],
                                  itotal,
                                  ototal,
                                  itotal+ototal
                                  ])
        # Once all the details has been saved to the excel.
        # Show some confirmation.
        # Declare also a location variable so that it can be
        # shown to the user where the file has been saved.
        location = "Report has been exported to csv file.\n\n" + "Location: " + os.getcwd()
        messagebox.showinfo('Information', location)

    def quitApp(self):
        """
        This method was created for properly shutting down
        the application. And for the database to close properly.
        """
        if self.database:
            self.cur.close()
            self.database.close()
            print('Database has been closed.')
        self.destroy()


class LicenseWindow(tk.Toplevel):

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title("License")
        self.protocol("WM_DELETE_WINDOW", self.quitApp)

        # Create the rest of the widget here.
        mainframe = tk.Frame(self)
        mainframe.pack(expand=True, fill='both')

        self.lic_text = scrolledtext.ScrolledText(mainframe)
        self.lic_text.pack(expand=True, fill='both')

        # Insert details.
        self.insertDetails()

        close_btn = ttk.Button(self, text='Close', command=self.quitApp)
        close_btn.pack(padx=5, pady=5)

    def insertDetails(self):
        lic_file = open("LICENSE", 'r')
        data = lic_file.read()
        lic_file.close()

        self.lic_text.insert('end', data)
        self.lic_text.config(state='disabled')

    def quitApp(self):
        self.destroy()


class AboutDialog(tk.Toplevel):

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title('About')
        self.protocol('WM_DELETE_WINDOW', self.quitApp)
        self.resizable(0, 0)
        container = tk.Frame(self)
        container.pack(fill='both', expand=True, padx=5, pady=5)
        self.grab_set()
        self.iconlocation = os.getcwd() + "/tsicon.ico"
        print(self.iconlocation)
        try:
            self.master.iconbitmap(self.iconlocation)
        except:
            pass
        # Create style.
        style = ttk.Style()
        style.configure('appname.TLabel',
                        font=('Curlz MT', 20, 'bold'),
                        foreground='red',
                        anchor='center'
                        )
        style.configure('ver.TLabel',
                        font=('Helvetica', 12, 'bold'),
                        foreground='blue',
                        anchor='center'
                        )
        style.configure('normal.TLabel',
                        font=('Helvetica', 11),
                        foreground='black',
                        anchor='center'
                        )
        # Add labels for application details.
        app_name = ttk.Label(container,
                             text=__appname__,
                             style='appname.TLabel'
                             )
        app_name.pack(fill='both')
        ver = ttk.Label(container,
                        text="version: "+__version__,
                        style='ver.TLabel'
                        )
        ver.pack(fill='both')
        desc = ttk.Label(container,
                         text=__description__,
                         style='normal.TLabel'
                         )
        desc.pack(fill='both')
        author = ttk.Label(container,
                           text='Author: '+__author__,
                           style='normal.TLabel'
                           )
        author.pack(fill='both')
        email = ttk.Label(container,
                          text='E-mail: '+__email__,
                          style='normal.TLabel'
                          )
        email.pack(fill='both')
        website = ttk.Label(container,
                            text='Web: '+__web__,
                            style='normal.TLabel'
                            )
        website.pack(fill='both')
        lic = ttk.Label(container,
                        text='License: '+__license__,
                        style='normal.TLabel'
                        )
        lic.pack(fill='both')
        close_button = ttk.Button(container,
                                  text='Close',
                                  command=self.quitApp
                                  )
        close_button.pack(anchor='e', padx=8, pady=8)
        close_button.focus_set()

    def quitApp(self):
        self.grab_release()
        self.destroy()


class MainWindow(tk.Frame):
    
    def __init__(self, master):
        """
        Initialize the graphics user interface for the main window of
        the application. It consist of menubar and 4 buttons for item
        master, incoming and outgoing transaction, and stock report.
        """
        tk.Frame.__init__(self, master)
        # Set the title and position of the window.
        self.master.title(" ".join([__appname__, __version__]))
        self.master.geometry("+100+100")
        self.master.protocol('WM_DELETE_WINDOW', self.quitApp)
        # Disable maximize window.
        self.master.resizable(0, 0)
        self.pack(fill='both', expand=True, padx=5, pady=5)
        self.iconlocation = os.getcwd() + "/tsicon.ico"
        try:
            self.master.iconbitmap(self.iconlocation)
        except:
            pass

        # Create menu bar of the main window.
        self.menubar = tk.Menu(self)
        self.master.config(menu=self.menubar)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.optionmenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.menubar.add_cascade(label='Option', menu=self.optionmenu)
        self.menubar.add_cascade(label='Help', menu=self.helpmenu)
        self.filemenu.add_command(label='Quit', command=self.quitApp)
        self.helpmenu.add_command(label='License', command=self.licenseWindow)
        self.helpmenu.add_command(label='Company', command=self.companydetails)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label='About', command=self.aboutDialog)
        self.optionmenu.add_command(label='Edit Company', command=self.updateDetails)

        # Create 4 buttons for item master, incoming, outgoing, and reports.
        self.item_master_btn = ttk.Button(self, text='Item Master',
                                          command=self.itemmaster
                                          )
        self.item_master_btn.grid(row=0, column=0)
        self.incoming_btn = ttk.Button(self, text='Incoming',
                                       command=self.incoming)
        self.incoming_btn.grid(row=0, column=1)
        self.outgoing_btn = ttk.Button(self, text='Outgoing',
                                       command=self.outgoing)
        self.outgoing_btn.grid(row=0, column=2)
        self.report_btn = ttk.Button(self, text='Reports',
                                     command=self.showReport)
        self.report_btn.grid(row=0, column=3)

        # Check whether database is available
        # if not create database and tables.
        if not os.path.isfile('inv_database.db'):
            self.setcompanydetails()

    def updateDetails(self):
        """
        This method is for updating the company details if there is a
        some changes needed to done for information puporses and make
        sure that the existing table has been deleted before creating
        a new table for company.
        """
        # Initialize the database and delete company table
        database = sqlite3.connect('inv_database.db')
        cur = database.cursor()
        cur.execute("DROP TABLE IF EXISTS company")
        cur.execute("""
            CREATE TABLE company(com_name TEXT,
                com_address TEXT,
                com_telephone TEXT,
                com_fax TEXT,
                com_email TEXT)
            """)
        self.setcompanydetails()
        self.save_button.grid_forget()
        self.update_button = ttk.Button(self.setcom_frame, text='Update')
        self.update_button.bind('<Button-1>', self.updatecomdetails)
        self.update_button.grid(row=5, column=1, sticky='e')
        if database:
            database.commit()
            cur.close()
            database.close()

    def setcompanydetails(self):
        """
        This is a toplevel tkinter window for adding or updating
        the company details.
        """
        self.setcom_tp = tk.Toplevel(self.master)
        self.setcom_tp.title('Enter Details')
        self.setcom_tp.protocol('WM_DELETE_WINDOW', self.cancelprogram)
        self.setcom_tp.tkraise(aboveThis=self.master)
        self.setcom_tp.grab_set()
        self.setcom_frame = ttk.LabelFrame(self.setcom_tp,
                                           text='Set Company Details'
                                           )
        self.setcom_frame.pack()
        self.com_name = ttk.Label(self.setcom_frame, text='Company Name:')
        self.com_name.grid(row=0, column=0)
        self.com_addr = ttk.Label(self.setcom_frame, text='Address:')
        self.com_addr.grid(row=1, column=0)
        self.com_tel = ttk.Label(self.setcom_frame, text='Telephone:')
        self.com_tel.grid(row=2, column=0)
        self.com_fax = ttk.Label(self.setcom_frame, text='Fax:')
        self.com_fax.grid(row=3, column=0)
        self.com_email = ttk.Label(self.setcom_frame, text='E-mail:')
        self.com_email.grid(row=4, column=0)

        # Add company details entry.
        self.com_name_entry = ttk.Entry(self.setcom_frame)
        self.com_name_entry.grid(row=0, column=1)
        self.com_addr_entry = ttk.Entry(self.setcom_frame)
        self.com_addr_entry.grid(row=1, column=1)
        self.com_tel_entry = ttk.Entry(self.setcom_frame)
        self.com_tel_entry.grid(row=2, column=1)
        self.com_fax_entry = ttk.Entry(self.setcom_frame)
        self.com_fax_entry.grid(row=3, column=1)
        self.com_email_entry = ttk.Entry(self.setcom_frame)
        self.com_email_entry.grid(row=4, column=1)

        # Create save button.
        self.save_button = ttk.Button(self.setcom_frame, text='Save')
        self.save_button.bind('<Button-1>', self.insertcomdetails)
        self.save_button.grid(row=5, column=1, sticky='e')

        # Set the focus to company name entry widget.
        self.com_name_entry.focus_set()

    def cancelprogram(self):
        """
        This method is for checking if company name
        is available. If not these will not create the
        database and instead exit from the application
        gracefully.
        """
        if self.com_name_entry.get() == '':
            self.setcom_tp.grab_release()
            self.setcom_tp.destroy()
            self.master.destroy()
        else:
            self.insert_name = self.com_name_entry.get()
            self.insert_addr = self.com_addr_entry.get()
            self.insert_tel = self.com_tel_entry.get()
            self.insert_fax = self.com_fax_entry.get()
            self.insert_email = self.com_email_entry.get()

            dbase = CreateDatabase(self.insert_name,
                                   self.insert_addr,
                                   self.insert_tel,
                                   self.insert_fax,
                                   self.insert_email
                                   )
            dbase.create()
            self.setcom_tp.grab_release()
            self.setcom_tp.destroy()

    def insertcomdetails(self, event):
        """
        This method is a bind event to a tkinter button widget so that
        if the save button has been pressed it will insert the details
        into the database and create the initial database of the program.
        """
        print(event)
        if self.com_name_entry.get() == '':
            self.setcom_tp.grab_release()
            self.setcom_tp.destroy()
            self.master.destroy()
        else:
            self.insert_name = self.com_name_entry.get()
            self.insert_addr = self.com_addr_entry.get()
            self.insert_tel = self.com_tel_entry.get()
            self.insert_fax = self.com_fax_entry.get()
            self.insert_email = self.com_email_entry.get()

            dbase = CreateDatabase(self.insert_name,
                                   self.insert_addr,
                                   self.insert_tel,
                                   self.insert_fax,
                                   self.insert_email
                                   )
            dbase.create()
            self.setcom_tp.grab_release()
            self.setcom_tp.destroy()

    def updatecomdetails(self, event):
        """
        This method will insert the new details for the company
        into the newly created table and close the user interface.
        """
        print(event)
        database = sqlite3.connect('inv_database.db')
        cur = database.cursor()
        cur.execute("INSERT INTO company VALUES(?, ?, ?, ?, ?)",
                    (self.com_name_entry.get(),
                     self.com_addr_entry.get(),
                     self.com_tel_entry.get(),
                     self.com_fax_entry.get(),
                     self.com_email_entry.get()))
        try:
            database.commit()
        except sqlite3.Error:
            database.rollback()

        if database:
            cur.close()
            database.close()

        self.setcom_tp.grab_release()
        self.setcom_tp.destroy()

    def aboutDialog(self):
        """
        This is where you can find the details of the application
        including the name of the app, version, author, email of
        the author, website and license.
        """
        AboutDialog(self)

    def itemmaster(self):
        """
        This method is for adding new items into the database to use
        in the application.
        """
        self.item_master_tp = tk.Toplevel(self.master)
        ItemMaster(self.item_master_tp)

    def incoming(self):
        """
        This method is for incoming transactions like deliveries or even
        stock adjustments.
        """
        self.incoming_tp = tk.Toplevel(self.master)
        ItemIn(self.incoming_tp)

    def licenseWindow(self):
        """
        This method is for incoming transactions like deliveries or even
        stock adjustments.
        """
        LicenseWindow(self)

    def outgoing(self):
        """
        This method is for outgoing transactions like issues/sales or even
        stock adjustments.
        """
        self.outgoing_tp = tk.Toplevel(self.master)
        ItemOut(self.outgoing_tp)

    def companydetails(self):
        """
        This is where the details for your company can be found including
        the name of the company, address, telephone and fax number, and
        e-mail provided at the start of the application.
        """
        self.com_details_tp = tk.Toplevel(self.master)
        CompanyDetails(self.com_details_tp)

    def showReport(self):
        """
        This method is for showing the user the stock reports for monitoring
        purposes.
        """
        Reports(self)

    def quitApp(self):
        """
        This method is for quitting your application gracefully.
        """
        self.master.destroy()


def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
