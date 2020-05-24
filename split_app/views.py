from django.shortcuts import redirect, render
from .models import Document
from .forms import DocumentForm

from rest_framework import status

from rest_framework import generics
from .serializers import DocumentSerializer
from rest_framework.response import Response
from .formatter import formatResponse
from django.conf import settings

import math
import os
from os.path import basename
import pathlib
import pandas as pd

from django.db import transaction
from zipfile import ZipFile
from django.http import HttpResponse, Http404

# import xlsxwriter module
import xlsxwriter


def index(request):
    return render(request, "split_app/index.html")


def downloadZip(request, document_id):
    try:
        document = Document.objects.get(pk=document_id)
        filePath = (
            settings.BASE_DIR + "/documents/output/archived/" + document.title + ".zip"
        )

        if os.path.exists(filePath):
            with open(filePath, "rb") as fh:
                response = HttpResponse(
                    fh.read(), content_type="application/vnd.ms-excel"
                )
                response[
                    "Content-Disposition"
                ] = "inline; filename=" + os.path.basename(filePath)
                return response
        else:
            return HttpResponse("Not Found")

    except Document.DoesNotExist:
        return HttpResponse("Not Found")


class SampleExcel(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        workbook = xlsxwriter.Workbook("sample.xlsx")
        worksheet = workbook.add_worksheet()
        row = 0
        for x in range(0, 10000):
            column = 0
            for y in range(0, 20):
                worksheet.write(row, column, str(x + y))
                column += 1

            row += 1

        workbook.close()

        return formatResponse("", status_code=status.HTTP_200_OK)


class DocumentCreate(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def post(self, request, *args, **kwargs):
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            document = form.save()

            try:
                readyForInsert = self._process_data_for_insertion(
                    document, request.POST
                )
                titleFolder = self._createTitledFile()
                self._writeFiles(document, readyForInsert)
                self.zipFiles()
            except ValueError as error:
                return formatResponse(
                    str(error), status_code=status.HTTP_400_BAD_REQUEST
                )
        else:
            return formatResponse(
                "The form is not valid {0} ".format(form.errors),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        zipLink = "/api/document/download/" + str(document.id)
        return formatResponse(zipLink, status_code=status.HTTP_200_OK)

    def zipFiles(self):
        with ZipFile(
            self.outputDir + "/archived/" + self.document.title + ".zip", "w"
        ) as zipObj:
            # iterate over all the files in the directory

            for folderName, subfolers, filenames in os.walk(
                self.outputDir + "/" + self.document.title
            ):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    # Add file to zip
                    zipObj.write(filePath, basename(filePath))

    def _writeFiles(self, document, data):
        index = 0

        titleEnd = 0
        for chunkedData in data:
            # Start from the first cell.
            # Rows and columns are zero indexed
            fileName = document.title + " #" + str(index) + ".xlsx"  # + self.extension
            filePath = self.outputDir + "/" + document.title + "/" + fileName
            workbook = xlsxwriter.Workbook(filePath)
            worksheet = workbook.add_worksheet()

            titleRow = 0
            titleColumn = 0
            if self.document.copy_headers:
                for title in self.headerTitles:
                    worksheet.write(titleRow, titleColumn, title)
                    titleColumn += 1

                # Where other rows should start from
                titleRow = 1

            index = index + 1
            row = titleRow
            column = 0
            for item in chunkedData:
                column = 0
                for itemValue in item:
                    # print(itemValue)
                    # move to the next column
                    if str(itemValue) == "nan" and math.isnan(float(itemValue)):
                        worksheet.write(row, column, "")
                    else:
                        worksheet.write(row, column, itemValue)
                    column += 1

                # move to the next row
                row += 1

            workbook.close()

    def _createTitledFile(self):

        # Create the root file if not exist
        try:
            os.mkdir(self.outputDir)
            os.mkdir(self.outputDir + "/archived")
        except OSError as error:
            pass
            # folder already created

        # Create Titled Folder
        try:
            titleFolder = self.outputDir + "/" + self.title
            os.mkdir(titleFolder)
            return titleFolder
        except OSError as error:
            if str(error).index("File exists") > 0:
                raise ValueError(
                    "There is a folder with that name {0}. ERRORDATA: FOLDER_EXIST {1} ".format(
                        self.title, str(error)
                    )
                )
            raise ValueError(str(error))
        pass

    def _process_data_for_insertion(self, document, docData):
        self.headerLoaded = False
        self.headerTitles = []
        self.data = []

        index = 0
        self.document = document
        self.title = document.title
        self.max_lines = document.max_lines
        index = index + 1

        # detect the extension
        extension = pathlib.Path(
            settings.BASE_DIR + document.docfile.url
        ).suffix.lower()
        is_csv = extension == ".csv"
        is_xlsx = extension == ".xlsx"
        self.extension = extension
        self.outputDir = settings.BASE_DIR + "/documents/output"
        sheet_name = document.sheet_name

        if len(sheet_name) == 0:
            sheet_name = "Sheet1"

        if is_csv:
            df = pd.read_csv(settings.BASE_DIR + document.docfile.url)
        elif is_xlsx:
            df = pd.read_excel(
                settings.BASE_DIR + document.docfile.url, sheet_name=sheet_name,
            )
        else:
            raise ValueError("Uknown file type")
        tuples = self._dataToTuple(df)
        totalRows = df.index.stop
        # print(totalRows >= 100 and document.max_lines / 1000 >= 1)
        # if totalRows >= 1000 or document.max_lines / totalRows >= 1:
        #     pass
        # else:
        #     document.delete()
        #     raise ValueError(
        #         "Please increase the maximum number of lines for each file"
        #     )

        maxLines = document.max_lines
        if self.document.count_headers:
            maxLines = document.max_lines - 1
        # chunkedData = self._chunkData(tuples, maxLines)
        chunkedData = self._chunkData2(tuples, maxLines)

        return chunkedData

    def _chunkData2(self, tupledData, maxLines):
        if maxLines > len(tupledData):
            maxLines = len(tupledData)

        allData = []
        done = False
        totalSize = len(tupledData)
        fromIndex = 0
        toIndex = maxLines
        while totalSize != 0:
            chunk = tupledData[fromIndex:toIndex]
            fromIndex += maxLines
            toIndex += maxLines
            totalSize -= len(chunk)
            allData.append(chunk)

        return allData

    def _chunkData(self, tupledData, maxLines):
        if maxLines > len(tupledData):
            maxLines = len(tupledData)
        counter = -1
        data = []
        maxData = []
        if self.document.copy_headers:
            maxData.append(self.headerTitles)

        for x in range(0, len(tupledData)):
            counter = counter + 1
            if counter == maxLines:
                data.append(maxData)
                # reset and add titles
                counter = 0
                maxData = []

                if self.document.copy_headers:
                    maxData.append(self.headerTitles)
                maxData.append(tupledData[x])
                data.append(maxData)

                if ((len(tupledData)) - 1) == x:
                    if self.document.copy_headers:
                        maxData.append(self.headerTitles)
                    maxData.append(tupledData[x])
                    data.append(maxData)

            else:
                if counter == maxLines:
                    if self.document.copy_headers:
                        maxData.append(self.headerTitles)
                    maxData.append(tupledData[x])
                maxData.append(tupledData[x])

        return data

    def _dataToTuple(self, df):
        totalRows = df.index.stop
        data = []
        for x in range(0, totalRows):
            theSeries = df.iloc[x]
            if len(self.headerTitles) == 0:
                for value in theSeries.index.values:
                    self.headerTitles.append(value)

            titleDatta = []
            for title in self.headerTitles:
                titleValue = theSeries.get(title)
                titleDatta.append(titleValue)
            data.append(titleDatta)

        return data

    def _getLength(self, df):
        print(df.iloc[0])
