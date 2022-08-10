"""Tests for the aimsun_input_utils script.

Throughout this file, tests are labeled in classes according to their object
type. The same groupings can be found at the bottom of the file for creating
test objects that are used within the unit tests. Note that some of the
functions may seem redundant, but they are meant to act as abstraction barriers;
the tests should only reference functions within this file.


The tests themselves also have their own labeling system. Anything labeled as
'test_[name]' tests the functionality of the object, such as file import/export.
Anything labeled as 'test_fail_[name]' tests the failure cases of an object,
such as incorrect data type or incorrect filepath information.
"""

from __future__ import annotations

import datetime
import os
import pickle
import random
import tempfile
from typing import Dict
import unittest
import warnings

import aimsun_input_utils


class TestCentroidConfiguration(unittest.TestCase):
    """Test the export_to_file() and _import_from_file() methods of
    the CentroidConfiguration class in aimsun_input_utils.py.

    This is done by checking that exporting and importing the same
    CentroidConfiguration object maintains equality with the original copy.
    Errors such as exporting empty CentroidConfiguration and importing from
    wrong files are tested by checking that Exceptions or Warnings are
    appropriately raised.
    """

    def test_object_creation(self):
        """Test that the CentroidConfiguration creates properly."""
        ccs1 = aimsun_input_utils.CentroidConfiguration()
        self.assertIsInstance(
            ccs1, aimsun_input_utils.CentroidConfiguration)
        ccs2 = _create_static_centroid_connections_object(
            random.randint(1, 99), random.randint(1, 99), random.randint(1, 99),
            random.randint(0, 1))
        self.assertIsInstance(
            ccs2, aimsun_input_utils.CentroidConfiguration)
        ccs3 = _create_random_centroid_connections_object(
            random.randint(0, 99))
        self.assertIsInstance(
            ccs3, aimsun_input_utils.CentroidConfiguration)

    def test_equality(self):
        """Test object equality of CentroidConfiguration objects."""
        ccs1 = _create_static_centroid_connections_object(5, 5, 5, 0)
        ccs2 = _create_static_centroid_connections_object(5, 5, 5, 0)
        ccs3 = _create_static_centroid_connections_object(5, 5, 1, 0)
        ccs4 = _create_static_centroid_connections_object(5, 1, 5, 0)
        ccs5 = _create_static_centroid_connections_object(1, 5, 5, 0)
        ccs6 = _create_static_centroid_connections_object(5, 5, 5, 1)
        ccs7 = aimsun_input_utils.CentroidConfiguration()
        self.assertTrue(ccs1.__eq__(ccs2))
        self.assertFalse(ccs1.__eq__(ccs3))
        self.assertFalse(ccs1.__eq__(ccs4))
        self.assertFalse(ccs1.__eq__(ccs5))
        self.assertFalse(ccs1.__eq__(ccs6))
        self.assertFalse(ccs1.__eq__(ccs7))

    def test_export_basic(self):
        """Test that exporting CentroidConfiguration objects work properly."""
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        ccs1 = _create_random_centroid_connections_object(
            random.randint(0, 99))
        ccs1.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_export_advanced(self):
        """Test that exporting different CentroidConfiguration objects do not
        satisify object equality unless it has the same attributes.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        ccs1 = _create_random_centroid_connections_object(
            random.randint(0, 99))
        ccs1.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        ccs2 = _create_random_centroid_connections_object(
            random.randint(0, 99))
        ccs2.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        ccs3 = aimsun_input_utils.CentroidConfiguration(filepath)
        self.assertEqual(ccs2, ccs3)
        self.assertNotEqual(ccs1, ccs3)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_export_import_equals(self):
        """Test that exporting and importing the same CentroidConfiguration
        objects satisifies object equality.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        ccs1 = _create_random_centroid_connections_object(
            random.randint(0, 99))
        ccs1.export_to_file(filepath)
        ccs2 = aimsun_input_utils.CentroidConfiguration(filepath)
        self.assertEqual(ccs1, ccs2)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_create_from_filepath(self):
        """Test that the same CentroidConfiguration is retrievable from a
        given filepath.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        ccs1 = _create_random_centroid_connections_object(
            random.randint(0, 99))
        ccs1.export_to_file(filepath)
        ccs2 = _create_centroid_connections_object_from_filepath(filepath)
        self.assertEqual(ccs1, ccs2)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_invalid_filepath_import(self):
        """Test that trying to retrieve a CentroidConfiguration with an invalid
        filepath will return an error.
        """
        filepath = 'This_is_not_a_valid_filepath'
        # Invalid filepath
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.CentroidConfiguration(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_empty_filepath_import(self):
        """Tests if code will raise a FileNotFound error for a syntactically
        valid filepath that doesn't point to a file.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.CentroidConfiguration(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_filetype(self):
        """Tests if the code will raise a ValueError for a filepath pointing
        to an invalid file extension.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.txt')
        with open(filepath, 'wb') as file:
            pickle.dump('Wrong filetype.', file)
        # Filetype is not '.pkl'
        with self.assertRaises(ValueError):
            aimsun_input_utils.CentroidConfiguration(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_object_type(self):
        """Tests if importing from wrong filetype will raise an an EOFError."""
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with open(filepath, 'wb') as file:
            pickle.dump(['Not a real ccs object'], file)
        # Not enough attributes in '.pkl' file to be a ccs object
        with self.assertRaises(EOFError):
            aimsun_input_utils.CentroidConfiguration(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_name_type(self):
        """Tests if importing a CentroidConfiguration object with the wrong name
        type will raise a TypeError.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with open(filepath, 'wb') as file:
            pickle.dump(777, file)
            pickle.dump(['Not a real ccs object'], file)
        # First attribute is not a string (External ID)
        with self.assertRaises(TypeError):
            aimsun_input_utils.CentroidConfiguration(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_list_type(self):
        """Tests if importing a CentroidConfiguration object with the wrong
        object type in its detector list will raise a TypeError.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with open(filepath, 'wb') as file:
            pickle.dump('Seems_to_be_a_name', file)
            pickle.dump(['Not a real ccs object'], file)
        # Second attribute is not a list of cc objects
        with self.assertRaises(TypeError):
            aimsun_input_utils.CentroidConfiguration(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_bad_export(self):
        """Test that exporting a CentroidConfiguration object with wrong types
        for its attributes will return an error and stop the export.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        # Test when first attribute is not a string (External ID)
        ccs1 = _create_random_centroid_connections_object(
            random.randint(0, 99))
        ccs1.external_id = 777
        with self.assertRaises(TypeError):
            ccs1.export_to_file(filepath)
        self.assertFalse(os.path.exists(filepath))
        # Test when second attribute is not a CentroidConnection object
        ccs2 = _create_random_centroid_connections_object(
            random.randint(0, 99))
        ccs2.external_id = 'valid_name'
        ccs2.centroid_connection_list = ['wrong_centroid_type']
        with self.assertRaises(TypeError):
            ccs2.export_to_file(filepath)
        self.assertFalse(os.path.exists(filepath))


class TestOriginDestinationMatrices(unittest.TestCase):
    """Test the export_to_file() and _import_from_file() methods of
    the OriginDestinationMatrices class in aimsun_input_utils.py.

    This is done by checking that exporting and importing the same
    OriginDestinationMatrices object maintains equality with the original copy.
    Errors such as exporting empty OriginDestinationMatrices and importing from
    wrong files are tested by checking that Exceptions or Warnings are
    appropriately raised.
    """

    def test_object_creation(self):
        """Tests that the OriginDestinationMatrices object creates properly."""
        odm1 = _create_random_od_matrices_object(random.randint(0, 99))
        self.assertTrue(odm1, aimsun_input_utils.OriginDestinationMatrix)
        odm2 = _create_static_od_matrices_object(
            random.randint(0, 99), random.randint(0, 11),
            random.randint(12, 23), random.random(), random.randint(0, 1))
        self.assertTrue(odm2, aimsun_input_utils.OriginDestinationMatrix)

    def test_equality(self):
        """Test object equality of OriginDestinationMatrices objects."""
        odm1 = _create_static_od_matrices_object(5, 5, 15, 100.0, 0)
        odm2 = _create_static_od_matrices_object(5, 5, 15, 100.0, 0)
        odm3 = _create_static_od_matrices_object(5, 5, 17, 100.0, 0)
        odm4 = _create_static_od_matrices_object(5, 1, 15, 100.0, 0)
        odm5 = _create_static_od_matrices_object(1, 5, 15, 100.0, 0)
        odm6 = _create_static_od_matrices_object(5, 5, 15, 150.0, 0)
        odm7 = _create_static_od_matrices_object(5, 5, 15, 100.0, 1)
        odm8 = aimsun_input_utils.OriginDestinationMatrices()
        self.assertTrue(odm1.__eq__(odm2))
        self.assertFalse(odm1.__eq__(odm3))
        self.assertFalse(odm1.__eq__(odm4))
        self.assertFalse(odm1.__eq__(odm5))
        self.assertFalse(odm1.__eq__(odm6))
        self.assertFalse(odm1.__eq__(odm7))
        self.assertFalse(odm1.__eq__(odm8))

    def test_export_basic(self):
        """Test that exporting OriginDestinationMatrices objects work properly.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        odm1 = _create_random_od_matrices_object(random.randint(0, 99))
        odm1.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_export_advanced(self):
        """Test that exporting different OriginDestinationMatrices objects do
        not satisify object equality unless it has the same attributes.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        odm1 = _create_random_od_matrices_object(random.randint(0, 99))
        odm1.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        odm2 = _create_random_od_matrices_object(random.randint(0, 99))
        odm2.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        odm3 = aimsun_input_utils.OriginDestinationMatrices(filepath)
        self.assertEqual(odm2, odm3)
        self.assertNotEqual(odm1, odm3)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_export_import_equals(self):
        """Test that exporting and importing the same OriginDestinationMatrices
        objects satisifies object equality.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        odm1 = _create_random_od_matrices_object(random.randint(0, 99))
        odm1.export_to_file(filepath)
        odm2 = aimsun_input_utils.OriginDestinationMatrices(filepath)
        self.assertEqual(odm1, odm2)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_create_from_filepath(self):
        """Test that the same OriginDestinationMatrices is retrievable from a
        given filepath.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        odm1 = _create_random_od_matrices_object(random.randint(0, 99))
        odm1.export_to_file(filepath)
        odm2 = _create_od_matrices_object_from_filepath(filepath)
        self.assertEqual(odm1, odm2)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_invalid_filepath_import(self):
        """Test that trying to retrieve a OriginDestinationMatrices with an
        invalid filepath will return an error.
        """
        filepath = 'This_is_not_a_valid_filepath'
        # Invalid filepath
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.OriginDestinationMatrices(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_empty_filepath_import(self):
        """Tests if code will raise a FileNotFound error for a syntactically
        valid filepath that doesn't point to a file.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.OriginDestinationMatrices(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_filetype(self):
        """Tests if the code will raise a ValueError for a filepath pointing
        to an invalid file extension.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.txt')
        with open(filepath, 'wb') as file:
            pickle.dump('Wrong filetype.', file)
        # Filetype is not '.pkl'
        with self.assertRaises(ValueError):
            aimsun_input_utils.OriginDestinationMatrices(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_object_type(self):
        """Tests if importing a OriginDestinationMatrices object with the wrong
        object type in its OriginDestinationMatrix list will raise a TypeError.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with open(filepath, 'wb') as file:
            pickle.dump(['Not a real odm object'], file)
            pickle.dump('external_id', file)
        # Not enough attributes in '.pkl' file to be an odm object
        with self.assertRaises(TypeError):
            aimsun_input_utils.OriginDestinationMatrices(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_list_type(self):
        """Tests if importing a OriginDestinationMatrices object with the wrong
        name type will raise a TypeError.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with open(filepath, 'wb') as file:
            pickle.dump(['Not a real odm object'], file)
            pickle.dump(aimsun_input_utils.VehicleTypeName.TRAVELER, file)
        # First attribute is not a list of odd objects
        with self.assertRaises(TypeError):
            aimsun_input_utils.OriginDestinationMatrices(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_bad_export(self):
        """Test that exporting a OriginDestinationMatrices object with wrong
        types for its attributes will return an error and stop the export.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        # Test when first attribute is not ExternalId type
        odm1 = _create_random_od_matrices_object(random.randint(0, 99))
        odm1.centroid_configuration_external_id = {'not a real': 'ID'}
        with self.assertRaises(TypeError):
            odm1.export_to_file(filepath)
        # Test when second attribute is not a VehicleType enumeration
        odm2 = _create_random_od_matrices_object(random.randint(0, 99))
        odm2.od_matrices[0].vehicle_type = 777
        with self.assertRaises(TypeError):
            odm2.export_to_file(filepath)
        # Test that no files were saved
        self.assertFalse(os.path.exists(filepath))


class TestSectionSpeedLimitsAndCapacities(unittest.TestCase):
    """Test the export_to_file() and _import_from_file() methods of
    the SectionSpeedLimitsAndCapacities class in aimsun_input_utils.py.

    This is done by checking that exporting and importing the same
    SectionSpeedLimitsAndCapacities object maintains equality with the original
    copy. Errors such as exporting empty SectionSpeedLimitsAndCapacities and
    importing from wrong files are tested by checking that Exceptions or
    Warnings are appropriately raised.
    """

    def test_object_creation(self):
        """Tests that the SectionSpeedLimitsAndCapacities object creates
        properly.
        """
        sslacs1 = _create_random_section_slacs_object(random.randint(0, 99))
        self.assertIsInstance(
            sslacs1, aimsun_input_utils.SectionSpeedLimitsAndCapacities)
        sslacs2 = _create_static_section_slacs_object(
            random.randint(0, 99), random.random() * 80.0,
            random.random() * 300.0)
        self.assertIsInstance(
            sslacs2, aimsun_input_utils.SectionSpeedLimitsAndCapacities)

    def test_equality(self):
        """Test object equality of SectionSpeedLimitsAndCapacities objects."""
        sslacs1 = _create_static_section_slacs_object(5, 50.0, 200.0)
        sslacs2 = _create_static_section_slacs_object(5, 50.0, 200.0)
        sslacs3 = _create_static_section_slacs_object(10, 50.0, 200.0)
        sslacs4 = _create_static_section_slacs_object(5, 70.0, 200.0)
        sslacs5 = _create_static_section_slacs_object(5, 50.0, 150.0)
        sslacs6 = aimsun_input_utils.SectionSpeedLimitAndCapacity()
        self.assertTrue(sslacs1.__eq__(sslacs2))
        self.assertFalse(sslacs1.__eq__(sslacs3))
        self.assertFalse(sslacs1.__eq__(sslacs4))
        self.assertFalse(sslacs1.__eq__(sslacs5))
        self.assertFalse(sslacs1.__eq__(sslacs6))

    def test_export_basic(self):
        """Test that exporting SectionSpeedLimitsAndCapacities objects work
        properly.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        sslacs1 = _create_random_section_slacs_object(random.randint(0, 99))
        sslacs1.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_export_advanced(self):
        """Test that exporting different SectionSpeedLimitsAndCapacities objects
        do not satisify object equality unless it has the same attributes.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        sslacs1 = _create_random_section_slacs_object(random.randint(0, 99))
        sslacs1.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        sslacs2 = _create_random_section_slacs_object(random.randint(0, 99))
        sslacs2.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        sslacs3 = aimsun_input_utils.SectionSpeedLimitsAndCapacities(filepath)
        self.assertEqual(sslacs2, sslacs3)
        self.assertNotEqual(sslacs1, sslacs3)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_export_import_equals(self):
        """Test that exporting and importing the same
        SectionSpeedLimitsAndCapacities objects satisifies object equality.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        sslacs1 = _create_random_section_slacs_object(random.randint(0, 99))
        sslacs1.export_to_file(filepath)
        sslacs2 = aimsun_input_utils.SectionSpeedLimitsAndCapacities(filepath)
        self.assertEqual(sslacs1, sslacs2)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_create_from_filepath(self):
        """Test that the same SectionSpeedLimitsAndCapacities is retrievable
        from a given filepath.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        sslacs1 = _create_random_section_slacs_object(random.randint(0, 99))
        sslacs1.export_to_file(filepath)
        sslacs2 = _create_section_slacs_object_from_filepath(filepath)
        self.assertEqual(sslacs1, sslacs2)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_invalid_filepath_import(self):
        """Test that trying to retrieve a SectionSpeedLimitsAndCapacities with
        an invalid filepath will return an error.
        """
        filepath = 'This_is_not_a_valid_filepath'
        # Invalid filepath
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.SectionSpeedLimitsAndCapacities(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_empty_filepath_import(self):
        """Tests if code will raise a FileNotFound error for a syntactically
        valid filepath that doesn't point to a file.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.SectionSpeedLimitsAndCapacities(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_filetype(self):
        """Tests if the code will raise a ValueError for a filepath pointing
        to an invalid file extension.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.txt')
        with open(filepath, 'wb') as file:
            pickle.dump('Wrong filetype.', file)
        # Filetype is not '.pkl'
        with self.assertRaises(ValueError):
            aimsun_input_utils.SectionSpeedLimitsAndCapacities(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_list_type(self):
        """Tests if importing a SectionSpeedLimitsAndCapacities object with the
        wrong name type will raise a TypeError.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with open(filepath, 'wb') as file:
            pickle.dump(['Not a real sslacs object'], file)
        # First attribute is not a list of sslac objects
        with self.assertRaises(TypeError):
            aimsun_input_utils.SectionSpeedLimitsAndCapacities(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_bad_export(self):
        """Test that exporting a SectionSpeedLimitsAndCapacities object with
        wrong types for its attributes will return an error and stop the export.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        # Test when first attribute is not a list of sslac objects
        sslacs1 = _create_random_section_slacs_object(random.randint(0, 99))
        sslacs1.speed_limit_and_capacity_list = 777
        with self.assertRaises(TypeError):
            sslacs1.export_to_file(filepath)
        self.assertFalse(os.path.exists(filepath))


class TestDetectors(unittest.TestCase):
    """Test of the aimsun_input_utils.Detectors class."""

    def test_detectors_export_create_file(self):
        """Verify whether export_to_file() creates a new file."""
        filepath = os.path.join(tempfile.gettempdir(), "detectors_1.pkl")
        detectors = _create_detectors(1)
        detectors.export_to_file(filepath)
        # Check if file was created at filepath
        self.assertTrue(os.path.exists(filepath))
        os.remove(filepath)

    def test_detectors_import_equals_export(self):
        """Verify that export_to_file() and _import_to_file() will
        return the same values."""
        filepath = os.path.join(tempfile.gettempdir(), "detectors_2.pkl")
        original_detectors = _create_detectors(10)
        original_detectors.export_to_file(filepath)
        # Import using constructor
        new_detectors = aimsun_input_utils.Detectors(filepath)
        os.remove(filepath)
        # Check if new_ditrs contains the same attributes as the original_ditrs
        self.assertTrue(new_detectors == original_detectors)
        # Check if new_ditrs is not equal to a different ditrs of same size
        different_detectors = _create_detectors(10)
        self.assertFalse(new_detectors == different_detectors)

    def test_detectors_export_existing_file(self):
        """Verify that export_to_file() raises a warning if a file
        already exists at given filepath."""
        filepath = os.path.join(tempfile.gettempdir(), "detectors_4.pkl")
        with open(filepath, 'wt', encoding='utf-8') as existing_file:
            existing_file.write("This file is existing.")
        detectors = _create_detectors(5)
        # Check if warning was raised for existing file
        with warnings.catch_warnings(record=True) as detector_warning:
            detectors.export_to_file(filepath)
            self.assertTrue(len(detector_warning) == 1)
        os.remove(filepath)

    def test_detectors_export_empty_dataset(self):
        """Verify that export_to_file() throws an exception when
        DetectorIdToRoadSections object has empty flow_data_set."""
        filepath = os.path.join(tempfile.gettempdir(), "detectors_4.pkl")
        empty_detectors = _create_detectors(0)
        # Check if exception was raised for empty aimsun_detector_locations
        with self.assertRaises(ValueError):
            empty_detectors.export_to_file(filepath)

    def test_detectors_import_wrong_file_serialized(self):
        """Verify that _import_from_file() throws an exception when
        given file contains wrong data type."""
        filepath = os.path.join(tempfile.gettempdir(), "detectors_5.pkl")
        with open(filepath, 'wb') as file:
            pickle.dump(["This is a wrong dataset"], file)
        # Check if exception was raised for wrong data type
        with self.assertRaises(TypeError):
            aimsun_input_utils.Detectors(filepath)
        os.remove(filepath)

    def test_detectors_import_wrong_file_unserialized(self):
        """Verify that _import_from_file() throws an exception when given
        file did not follow serialization protocols at export_to_file()."""
        filepath = os.path.join(tempfile.gettempdir(), "detectors_6.pkl")
        with open(filepath, 'wt', encoding='utf-8') as wrong_file:
            wrong_file.write("This is not a serialized detector flow data")
        # Check if exception was raised for wrong serialization
        with self.assertRaises(pickle.UnpicklingError):
            aimsun_input_utils.Detectors(filepath)
        os.remove(filepath)

    def test_detector_equality_correct(self):
        """Check that Detector equality is correct for equality."""
        flow_detector_1 = aimsun_input_utils.Detector()
        flow_detector_1.external_id = 'city_detector_1'
        flow_detector_1.aimsun_section_internal_id = 12
        flow_detector_2 = aimsun_input_utils.Detector()
        flow_detector_2.external_id = 'city_detector_1'
        flow_detector_2.aimsun_section_internal_id = 12
        self.assertEqual(flow_detector_1, flow_detector_2)

    def test_detector_equality_not_correct(self):
        """Check that Detector equality is correct for inequality."""
        flow_detector_1 = aimsun_input_utils.Detector()
        flow_detector_1.external_id = 'city_detector_1'
        flow_detector_1.aimsun_section_internal_id = 12
        flow_detector_2 = aimsun_input_utils.Detector()
        flow_detector_2.external_id = 'city_detector_2'
        flow_detector_2.aimsun_section_internal_id = 13
        self.assertNotEqual(flow_detector_1, flow_detector_2)


class TestMasterControlPlan(unittest.TestCase):
    """Test the export_to_file() and __import_to_file() methods of the
    MasterControlPlan class in aimsun_input_utils.py."""

    def test_object_creation(self):
        """Tests that the MasterControlPlan object creates properly."""
        mcp1 = _create_static_master_control_plan_object(1, 10)
        self.assertTrue(mcp1, aimsun_input_utils.MasterControlPlan)
        mcp2 = _create_static_master_control_plan_object(5, 200)
        self.assertTrue(mcp2, aimsun_input_utils.MasterControlPlan)

    def test_equality(self):
        """Test object equality of MasterControlPlan objects."""
        mcp1 = _create_static_master_control_plan_object(3, 24)
        mcp2 = _create_static_master_control_plan_object(3, 24)
        mcp3 = _create_static_master_control_plan_object(5, 24)
        mcp4 = _create_static_master_control_plan_object(3, 10)
        mcp5 = _create_static_master_control_plan_object(10, 100)
        centconfig = aimsun_input_utils.CentroidConfiguration()
        self.assertTrue(mcp1.__eq__(mcp2))
        self.assertFalse(mcp1.__eq__(mcp3))
        self.assertFalse(mcp1.__eq__(mcp4))
        self.assertFalse(mcp1.__eq__(mcp5))
        self.assertFalse(mcp1.__eq__(centconfig))

    def test_export_basic(self):
        """Test that exporting MasterControlPlan objects work properly."""
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        mcp1 = _create_static_master_control_plan_object(3, 24)
        mcp1.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_export_advanced(self):
        """Test that exporting different MasterControlPlan objects do
        not satisify object equality unless it has the same attributes.
        """
        mcp1_filepath = os.path.join(os.getcwd(), 'test_pickle_1.pkl')
        mcp2_filepath = os.path.join(os.getcwd(), 'test_pickle_2.pkl')
        mcp1 = _create_static_master_control_plan_object(3, 24)
        mcp1.export_to_file(mcp1_filepath)
        self.assertTrue(os.path.exists(mcp1_filepath))
        mcp2 = _create_static_master_control_plan_object(5, 20)
        mcp2.export_to_file(mcp2_filepath)
        self.assertTrue(os.path.exists(mcp2_filepath))
        mcp3 = aimsun_input_utils.MasterControlPlan(mcp2_filepath)
        self.assertEqual(mcp2, mcp3)
        self.assertNotEqual(mcp1, mcp3)
        os.remove(mcp1_filepath)
        os.remove(mcp2_filepath)
        self.assertFalse(os.path.exists(mcp1_filepath))
        self.assertFalse(os.path.exists(mcp2_filepath))

    def test_export_import_equals(self):
        """Test that exporting and importing the same MasterControlPlan objects
        maintains object equality.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        mcp1 = _create_static_master_control_plan_object(3, 24)
        mcp1.export_to_file(filepath)
        mcp2 = aimsun_input_utils.MasterControlPlan(filepath)
        self.assertEqual(mcp1, mcp2)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_invalid_filepath_import(self):
        """Test that trying to retrieve a MasterControlPlan with an invalid
        filepath will return an error.
        """
        filepath = 'This_is_not_a_valid_filepath'
        # Invalid filepath
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.MasterControlPlan(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_empty_filepath_import(self):
        """Tests if code will raise a FileNotFound error for a syntactically
        valid filepath that doesn't point to a file.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.MasterControlPlan(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_filetype(self):
        """Tests if the code will raise a ValueError for a filepath pointing
        to an invalid file extension.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.txt')
        with open(filepath, 'wb') as file:
            for _ in range(6):  # Six attributes to save for MasterControlPlan
                pickle.dump('Wrong filetype', file)
        # Filetype is not '.pkl'
        with self.assertRaises(TypeError):
            aimsun_input_utils.MasterControlPlan(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_list_type(self):
        """Tests if importing a MasterControlPlan object with the wrong list
        type will raise a TypeError.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        datasize = 10
        with open(filepath, 'wb') as file:
            pickle.dump(['Not a real tms object'], file)
            pickle.dump([
                aimsun_input_utils.MasterControlPlanItem()
                for _ in range(datasize)], file)
            pickle.dump([
                aimsun_input_utils.ControlPlan() for _ in range(datasize)],
                file)
            pickle.dump([
                aimsun_input_utils.Metering() for _ in range(datasize)], file)
            pickle.dump([
                aimsun_input_utils.Detector() for _ in range(datasize)], file)
            pickle.dump('external_id', file)
            pickle.dump('name', file)
        # First attribute is not a list of tms objects
        with self.assertRaises(TypeError):
            aimsun_input_utils.MasterControlPlan(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_bad_export(self):
        """Test that exporting a MasterControlPlan object with wrong types for
        its attributes will return an error and stop the export.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        # Test when MasterControlPlan has wrong schedule list type
        wrong_schedule_mcp = _create_static_master_control_plan_object(1, 24)
        wrong_schedule_mcp.schedule = [111]
        with self.assertRaises(TypeError):
            wrong_schedule_mcp.export_to_file(filepath)
        # Test when MasterControlPlan has wrong control plan list type
        wrong_cont_plan_mcp = _create_static_master_control_plan_object(2, 24)
        wrong_cont_plan_mcp.control_plans = [222]
        with self.assertRaises(TypeError):
            wrong_cont_plan_mcp.export_to_file(filepath)
        # Test when MasterControlPlan has wrong meterings list type
        wrong_meterings_mcp = _create_static_master_control_plan_object(3, 24)
        wrong_meterings_mcp.meterings = [333]
        with self.assertRaises(TypeError):
            wrong_meterings_mcp.export_to_file(filepath)
        # Test when MasterControlPlan has wrong detectors list type
        wrong_detectors_mcp = _create_static_master_control_plan_object(4, 24)
        wrong_detectors_mcp.detectors = [444]
        with self.assertRaises(TypeError):
            wrong_detectors_mcp.export_to_file(filepath)
        # Test when MasterControlPlan has wrong external ID type
        wrong_ext_id_mcp = _create_static_master_control_plan_object(5, 24)
        wrong_ext_id_mcp.external_id = 555
        with self.assertRaises(TypeError):
            wrong_ext_id_mcp.export_to_file(filepath)
        # Test when MasterControlPlan has wrong name type
        wrong_name_mcp = _create_static_master_control_plan_object(6, 24)
        wrong_name_mcp.name = 666
        with self.assertRaises(TypeError):
            wrong_name_mcp.export_to_file(filepath)
        self.assertFalse(os.path.exists(filepath))


class TestTrafficManagementStrategies(unittest.TestCase):
    """Test the export_to_file() and __import_to_file() methods of the
    TrafficManagementStrategies class in aimsun_input_utils.py."""

    def test_object_creation(self):
        """Tests that the TrafficManagementStrategies object creates properly.
        """
        tms1 = _create_random_traffic_management_strategy_object(
            random.randint(1, 99), random.randint(1, 99))
        self.assertTrue(tms1, aimsun_input_utils.TrafficManagementStrategy)
        tms2 = _create_static_traffic_management_strategy_object(
            random.randint(1, 99), random.randint(1, 99), random.randint(1, 19),
            "text_obj" + str(random.randint(0, 9999)))
        self.assertTrue(tms2, aimsun_input_utils.TrafficManagementStrategy)

    def test_equality(self):
        """Test object equality of TrafficManagementStrategies objects."""
        tms1 = _create_static_traffic_management_strategy_object(
            15, 15, 6, "ext_id1")
        tms2 = _create_static_traffic_management_strategy_object(
            15, 15, 6, "ext_id1")
        tms3 = _create_static_traffic_management_strategy_object(
            12, 15, 6, "ext_id1")
        tms4 = _create_static_traffic_management_strategy_object(
            15, 12, 6, "ext_id1")
        tms5 = _create_static_traffic_management_strategy_object(
            15, 15, 1, "ext_id1")
        tms6 = _create_static_traffic_management_strategy_object(
            15, 15, 6, "ext_id8")
        tms7 = aimsun_input_utils.CentroidConfiguration()
        self.assertTrue(tms1.__eq__(tms2))
        self.assertFalse(tms1.__eq__(tms3))
        self.assertFalse(tms1.__eq__(tms4))
        self.assertFalse(tms1.__eq__(tms5))
        self.assertFalse(tms1.__eq__(tms6))
        self.assertFalse(tms1.__eq__(tms7))

    def test_export_basic(self):
        """Test that exporting TrafficManagementStrategies objects work
        properly.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        tms1 = _create_random_traffic_management_strategy_object(
            random.randint(0, 99), random.randint(0, 99))
        tms1.export_to_file(filepath)
        self.assertTrue(os.path.exists(filepath))
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_export_advanced(self):
        """Test that exporting different TrafficManagementStrategy objects do
        not satisify object equality unless it has the same attributes.
        """
        tms1_filepath = os.path.join(os.getcwd(), 'test_pickle_1.pkl')
        tms2_filepath = os.path.join(os.getcwd(), 'test_pickle_2.pkl')
        tms1 = _create_random_traffic_management_strategy_object(
            random.randint(1, 99), random.randint(1, 99))
        tms1.export_to_file(tms1_filepath)
        self.assertTrue(os.path.exists(tms1_filepath))
        tms2 = _create_random_traffic_management_strategy_object(
            random.randint(1, 99), random.randint(1, 99))
        tms2.export_to_file(tms2_filepath)
        self.assertTrue(os.path.exists(tms2_filepath))
        tms3 = aimsun_input_utils.TrafficManagementStrategy(tms2_filepath)
        self.assertEqual(tms2, tms3)
        self.assertNotEqual(tms1, tms3)
        os.remove(tms1_filepath)
        os.remove(tms2_filepath)
        self.assertFalse(os.path.exists(tms1_filepath))
        self.assertFalse(os.path.exists(tms2_filepath))

    def test_export_import_equals(self):
        """Test that exporting and importing the same TrafficManagementStrategy
        objects satisifies object equality.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        tms1 = _create_random_traffic_management_strategy_object(
            random.randint(1, 99), random.randint(1, 99))
        tms1.export_to_file(filepath)
        tms2 = aimsun_input_utils.TrafficManagementStrategy(filepath)
        self.assertEqual(tms1, tms2)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_create_from_filepath(self):
        """Test that the same TrafficManagementStrategy is retrievable from a
        given filepath.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        tms1 = _create_random_traffic_management_strategy_object(
            random.randint(1, 99), random.randint(1, 99))
        tms1.export_to_file(filepath)
        tms2 = _create_traffic_management_strategy_from_filepath(filepath)
        self.assertEqual(tms1, tms2)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_invalid_filepath_import(self):
        """Test that trying to retrieve a TrafficManagementStrategy with an
        invalid filepath will return an error.
        """
        filepath = 'This_is_not_a_valid_filepath'
        # Invalid filepath
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.TrafficManagementStrategy(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_empty_filepath_import(self):
        """Tests if code will raise a FileNotFound error for a syntactically
        valid filepath that doesn't point to a file.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with self.assertRaises(FileNotFoundError):
            aimsun_input_utils.TrafficManagementStrategy(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_filetype(self):
        """Tests if the code will raise a ValueError for a filepath pointing
        to an invalid file extension.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.txt')
        with open(filepath, 'wb') as file:
            pickle.dump('Wrong filetype', file)
            pickle.dump('Wrong filetype', file)
        # Filetype is not '.pkl'
        with self.assertRaises(ValueError):
            aimsun_input_utils.TrafficManagementStrategy(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_import_wrong_list_type(self):
        """Tests if importing a TrafficManagementStrategy object with the wrong
        list type will raise a TypeError.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        with open(filepath, 'wb') as file:
            pickle.dump(['Not a real tms object'], file)
            pickle.dump('name', file)
            pickle.dump('external_id', file)
        # First attribute is not a list of tms objects
        with self.assertRaises(TypeError):
            aimsun_input_utils.TrafficManagementStrategy(filepath)
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_fail_bad_export(self):
        """Test that exporting a TrafficManagementStrategy object with wrong
        types for its attributes will return an error and stop the export.
        """
        filepath = os.path.join(os.getcwd(), 'test_pickle.pkl')
        tms1 = _create_random_traffic_management_strategy_object(
            random.randint(1, 99), random.randint(1, 99))
        tms1.policies = 777
        # Test when first attribute is not a full list of Policies object type
        with self.assertRaises(TypeError):
            tms1.export_to_file(filepath)
        self.assertFalse(os.path.exists(filepath))


class TestAimsunFlowRealDataSet(unittest.TestCase):
    """Test the export_to_file() and _import_from_file() methods
    of the AimsunFlowRealDataSet() class in flow_processed_output.py.

    This is done by checking that exporting and importing the same
    AimsunFlowRealDataSet instance maintains equality with the original copy.
    Errors such as exporting empty AimsunFlowRealDataSet and importing from
    wrong files are tested by checking that Exceptions or Warnings are
    appropriately raised.
    """

    def test_output_flow_datset_export_create_file(self):
        """Verify whether export_to_file() creates a new file."""
        filepath = '1.txt'
        output_flow_datset = _create_random_flow_dataset(1)
        output_flow_datset.export_to_file(filepath)
        # Check if file was created at filepath
        self.assertTrue(os.path.exists(filepath))
        os.remove(filepath)

    def test_output_flow_datset_import_equals_export(self):
        """Verify that export_to_file() and _import_to_file() will
        return the same values."""
        filepath = '2.txt'
        original_output_flow_datset = _create_random_flow_dataset(10)
        original_output_flow_datset.export_to_file(filepath)
        # Import using constructor
        new_output_flow_datset = aimsun_input_utils.AimsunFlowRealDataSet(
            filepath)
        os.remove(filepath)
        # Check if new_output_flow_datset contains the same attributes as the
        # original_output_flow_datset.
        self.assertTrue(new_output_flow_datset == original_output_flow_datset)
        # Check if new_output_flow_datset is not equal to a different
        # output_flow_datset of same size.
        different_output_flow_datset = _create_random_flow_dataset(10)
        self.assertFalse(new_output_flow_datset == different_output_flow_datset)

    def test_output_flow_datset_export_existing_file(self):
        """Verify that export_to_file() raises a warning if a file
        already exists at given filepath."""
        filepath = '3.txt'
        with open(filepath, 'wt', encoding='utf-8') as existing_file:
            existing_file.write("This file is existing.")
        output_flow_datset = _create_random_flow_dataset(5)
        # Check if warning was raised for existing file
        with warnings.catch_warnings(record=True) as output_flow_datset_warning:
            output_flow_datset.export_to_file(filepath)
            self.assertTrue(len(output_flow_datset_warning) == 1)
        os.remove(filepath)

    def test_output_flow_datset_export_empty_dataset(self):
        """Verify that export_to_file() throws an exception when
        AimsunFlowRealDataSet object has empty flow_data_set."""
        filepath = '4.txt'
        empty_output_flow_datset = _create_random_flow_dataset(0)
        # Check if exception was raised for empty flow_data_set
        with self.assertRaises(Exception):
            empty_output_flow_datset.export_to_file(filepath)

    def test_output_flow_datset_import_wrong_file_serialized(self):
        """Verify that _import_from_file() throws an exception when
        given file contains wrong data type."""
        filepath = '5.txt'
        with open(filepath, 'wb') as file:
            pickle.dump(["This is a wrong dataset"], file)
        # Check if exception was raised for wrong data type
        with self.assertRaises(Exception):
            aimsun_input_utils.AimsunFlowRealDataSet(filepath)
        os.remove(filepath)

    def test_output_flow_datset_import_wrong_file_unserialized(self):
        """Verify that _import_from_file() throws an exception when given
        file did not follow serialization protocols at export_to_file()."""
        filepath = '6.txt'
        with open(filepath, 'xt', encoding='utf-8') as wrong_file:
            wrong_file.write("This is not a serialized detector flow data")
        # Check if exception was raised for wrong serialization
        with self.assertRaises(Exception):
            aimsun_input_utils.AimsunFlowRealDataSet(filepath)
        os.remove(filepath)

    def test_equality(self):
        """Verify object equality works between distinct AimsunFlowRealDataSet
        objects if they have the same attributes."""
        fds1 = _create_static_flow_dataset(
            10, 'detector_A', '1500', 'dataset_one', 'one.csv', 1)
        fds2 = _create_static_flow_dataset(
            10, 'detector_A', '1500', 'dataset_one', 'one.csv', 1)
        fds3 = _create_static_flow_dataset(
            99, 'detector_A', '1500', 'dataset_one', 'one.csv', 1)
        fds4 = _create_static_flow_dataset(
            10, 'detector_B', '1500', 'dataset_one', 'one.csv', 1)
        fds5 = _create_static_flow_dataset(
            10, 'detector_A', '7777', 'dataset_one', 'one.csv', 1)
        fds6 = _create_static_flow_dataset(
            10, 'detector_A', '1500', 'dataset_two', 'one.csv', 1)
        fds7 = _create_static_flow_dataset(
            10, 'detector_A', '1500', 'dataset_one', 'two.csv', 1)
        fds8 = _create_static_flow_dataset(
            10, 'detector_A', '1500', 'dataset_one', 'one.csv', 2)
        self.assertEqual(fds1, fds2)
        self.assertNotEqual(fds1, fds3)
        self.assertNotEqual(fds1, fds4)
        self.assertNotEqual(fds1, fds5)
        self.assertNotEqual(fds1, fds6)
        self.assertNotEqual(fds1, fds7)
        self.assertNotEqual(fds1, fds8)


def _generate_output_flow_data():
    """Generate flow data for a detector."""
    # Generate random detector_id
    random_detector_external_id = generate_random_external_id()
    # Generate random section_id
    random_section_id = random.randint(0, 9999)
    assert isinstance(random_section_id, int)
    # Generate random flow_data
    random_flow_data = generate_random_flowdata()
    # Create AimsunFlowRealDataSet with above parameters
    random_output_flow_data = aimsun_input_utils.FlowRealData()
    random_output_flow_data.external_id = random_detector_external_id
    random_output_flow_data.aimsun_section_internal_id = random_section_id
    random_output_flow_data.flow_data = random_flow_data
    assert isinstance(random_output_flow_data,
                      aimsun_input_utils.FlowRealData)
    return random_output_flow_data


def _create_random_flow_dataset(
    datasize: int
) -> aimsun_input_utils.AimsunFlowRealDataSet:
    """Generate random AimsunFlowRealDataSet.

    Args:
        datasize: Number of data in dataset.
    Returns:
        output_flow_dataset: Randomly generated AimsunFlowRealDataSet.
    """
    dataset = []
    for _ in range(datasize):
        output_flow_data = _generate_output_flow_data()
        dataset.append(output_flow_data)
    assert len(dataset) == datasize
    output_flow_dataset = aimsun_input_utils.AimsunFlowRealDataSet()
    output_flow_dataset.flow_data_set = dataset
    output_flow_dataset.external_id = "Fremont real data set."
    output_flow_dataset.filename = "aimsun_file.csv"
    output_flow_dataset.line_to_skip = 1
    return output_flow_dataset


def _create_static_flow_dataset(
    datasize: int, detector_ext_id: str, detector_int_id: str,
    dataset_ext_id: str, filename: str, skip_line: int
) -> aimsun_input_utils.AimsunFlowRealDataSet:
    """Generate static AimsunFlowRealDataSet with attributes defined by input.

    Args:
        datasize: Number of data in the flow dataset.
        detector_ext_id: External ID of the detectors.
        detector_int_id: Aimsun section internal ID of the detectors.
        dataset_ext_id: External ID of the flow dataset.
        filename: Filename of the flow dataset.
        skip_line: Line to skip in the flow dataset.
    Returns:
        output_flow_dataset: Static generated AimsunFlowRealDataSet with
            attributed defined by the input parameters.
    """
    # Default static FlowRealData object
    default_flow_data = aimsun_input_utils.FlowRealData()
    default_flow_data.external_id = detector_ext_id
    default_flow_data.aimsun_section_internal_id = detector_int_id
    default_flow_data.flow_data = {
        datetime.datetime(2022, 1, 1, 00, 00, 00): 1}

    # Create static AimsunFlowRealDataSet object
    dataset = [default_flow_data for _ in range(datasize)]
    output_flow_dataset = aimsun_input_utils.AimsunFlowRealDataSet()
    output_flow_dataset.flow_data_set = dataset
    output_flow_dataset.external_id = dataset_ext_id
    output_flow_dataset.filename = filename
    output_flow_dataset.line_to_skip = skip_line
    return output_flow_dataset


def _create_centroid_connections_object_from_filepath(
    filepath: str
) -> aimsun_input_utils.CentroidConfiguration:
    """Create a CentroidConfiguration object from given filepath.

    Args:
        filepath: Path to file that contains the CentroidConfiguration object.
    Returns:
        centroid_configuration: Recovered CentroidConfiguration from the input
            filepath.
    """
    assert len(filepath) > 0
    return aimsun_input_utils.CentroidConfiguration(filepath)


def _create_static_centroid_connections_object(
    num_centroids: int, num_centroids_from: int, num_centroids_to: int,
    c_type: int
) -> aimsun_input_utils.CentroidConfiguration:
    """Create and return a static CentroidConfiguration object with parameters
    defined by the input.

    Args:
        num_centroids: Total number of centroids in the CentroidConfiguration
            object.
        num_centroids_from: Number of origin centroids.
        num_centroids_to: Number of destination centroids.
        c_type: Type of centroid. See aimsun_input_utils.CentroidType for type
            definition.
    Returns:
        ccs_obj: CentroidConfiguration object initialized with the input
            parameters described above.
    """
    assert c_type in [0, 1]
    ccs_obj = aimsun_input_utils.CentroidConfiguration()
    ccs_obj.external_id = 'ccs_test_obj'
    ccs_obj.centroid_connection_list = []
    centroid_types = [aimsun_input_utils.CentroidType.INTERNAL,
                      aimsun_input_utils.CentroidType.EXTERNAL]
    for i in range(num_centroids):
        cc_obj = aimsun_input_utils.CentroidConnection()
        cc_obj.center_latitude_epsg_32610 = i
        cc_obj.center_longitude_epsg_32610 = i
        cc_obj.external_id = 'cc_test_obj' + str(i)
        cc_obj.centroid_type = centroid_types[c_type]
        cc_obj.from_section_internal_ids = []
        cc_obj.to_section_internal_ids = []
        for j in range(num_centroids_from):
            cc_obj.from_section_internal_ids.append(j)
        for k in range(num_centroids_to):
            cc_obj.to_section_internal_ids.append(k)
        ccs_obj.centroid_connection_list.append(cc_obj)
    return ccs_obj


def _create_random_centroid_connections_object(
    num_centroids: int, name: str = 'ccs_test_obj'
) -> aimsun_input_utils.CentroidConfiguration:
    """Create and return a random CentroidConfiguration object with parameters
    defined by the input.

    Args:
        num_centroids: Number of total centroids to generate in the
            CentroidConfiguration object.
        name: Name of the CentroidConfiguration object.
    Returns:
        ccs_obj: Randomly generated CentroidConfiguration object following the
            input parameters given above.
    """
    ccs_obj = aimsun_input_utils.CentroidConfiguration()
    ccs_obj.external_id = name
    ccs_obj.centroid_connection_list = []
    centroid_types = [aimsun_input_utils.CentroidType.INTERNAL,
                      aimsun_input_utils.CentroidType.EXTERNAL]
    for i in range(num_centroids):
        cc_obj = aimsun_input_utils.CentroidConnection()
        cc_obj.center_latitude_epsg_32610 = random.random() * 50
        cc_obj.center_longitude_epsg_32610 = random.random() * 50
        cc_obj.external_id = 'cc_test_obj' + str(i)
        cc_obj.centroid_type = centroid_types[random.randint(0, 1)]
        num_centroids_from = random.randint(0, 99)
        num_centroids_to = random.randint(0, 99)
        cc_obj.from_section_internal_ids = []
        cc_obj.to_section_internal_ids = []
        for _ in range(num_centroids_from):
            cc_obj.from_section_internal_ids.append(random.randint(0, 9999))
        for _ in range(num_centroids_to):
            cc_obj.to_section_internal_ids.append(random.randint(0, 9999))
        ccs_obj.centroid_connection_list.append(cc_obj)
    return ccs_obj


def _create_od_matrices_object_from_filepath(
    filepath: str
) -> aimsun_input_utils.OriginDestinationMatrices:
    """Return an OriginDestinationMatrices object given its file location.

    Args:
        filepath: Path to the file that contains the serialized
            OriginDestinationMatrices object.
    Returns:
        od_matrices: Recovered OriginDestinationMatrices from given filepath.
    """
    assert len(filepath) > 0
    return aimsun_input_utils.OriginDestinationMatrices(filepath)


def _create_static_od_matrices_object(
    num_od_matrices: int, start_time: int, end_time: int, trip_num: float,
    o_type: int
) -> aimsun_input_utils.OriginDestinationMatrices:
    """Return an OriginDestinationMatrices object given its file location.

    Args:
        filepath: Path to the file that contains the serialized
            OriginDestinationMatrices object.
    Returns:
        od_matrices: Recovered OriginDestinationMatrices from given filepath.
    """
    assert o_type in [0, 1]
    assert 0 <= start_time <= 11
    assert 12 <= end_time <= 23
    odm_obj = aimsun_input_utils.OriginDestinationMatrices()
    vehicle_types = [aimsun_input_utils.VehicleTypeName.RESIDENT,
                     aimsun_input_utils.VehicleTypeName.TRAVELER]
    odm_obj.od_matrices = []
    for _ in range(num_od_matrices):
        odd_obj = aimsun_input_utils.OriginDestinationMatrix()
        odd_obj.begin_time_interval = datetime.time(start_time, 0, 0)
        odd_obj.end_time_interval = datetime.time(end_time, 0, 0)
        trip_list = []
        od_trip = aimsun_input_utils.OriginDestinationTripsCount()
        od_trip.num_trips = trip_num
        od_trip.destination_centroid_external_id = 'dest_centroid'
        od_trip.origin_centroid_external_id = 'origin_centroid'
        trip_list.append(od_trip)
        odd_obj.od_trips_count = trip_list
        odd_obj.vehicle_type = vehicle_types[o_type]
        odm_obj.od_matrices.append(odd_obj)
    return odm_obj


def _create_random_od_matrices_object(
    num_odds: int
) -> aimsun_input_utils.OriginDestinationMatrices:
    """Create a random OriginDestinationMatrices object defined by input
    parameters.

    Args:
        num_odds: Number of OriginDestinationMatrix objects to be generated.
    Returns:
        odm_obj: Randomly generated OriginDestinationMatrices object.
    """
    odm_obj = aimsun_input_utils.OriginDestinationMatrices()
    odm_obj.od_matrices = []
    for _ in range(num_odds):
        odd_obj = aimsun_input_utils.OriginDestinationMatrix()
        odd_obj.begin_time_interval = datetime.time(
            random.randint(0, 11), random.randint(0, 59),
            random.randint(0, 59))
        odd_obj.end_time_interval = datetime.time(
            random.randint(12, 23), random.randint(0, 59),
            random.randint(0, 59))
        trip_list = []
        for _ in range(random.randint(0, 10)):
            od_trip = aimsun_input_utils.OriginDestinationTripsCount()
            od_trip.num_trips = random.random() * 50
            od_trip.destination_centroid_external_id = 'dest_centroid'
            od_trip.origin_centroid_external_id = 'origin_centroid'
            trip_list.append(od_trip)
        odd_obj.od_trips_count = trip_list
        odd_obj.vehicle_type = random.choice(
            [aimsun_input_utils.VehicleTypeName.RESIDENT,
             aimsun_input_utils.VehicleTypeName.TRAVELER])
        odm_obj.od_matrices.append(odd_obj)
    return odm_obj


def _create_static_master_control_plan_object(
    datasize: int, generator_id: int
) -> aimsun_input_utils.MasterControlPlan:
    """Generate a static MasterControlPlan with attributes defined by input.

    Attributes:
        datasize: Size of the data for its attributes.
        generator_id: Unique generation ID for its attributes.
    Returns:
        mcp: Static generated MasterControlPlan object.
    """
    # Create default subattribute objects
    default_control_junction = aimsun_input_utils.ControlJunction()
    default_control_junction.node_id = str(generator_id)
    default_control_junction.junction_type = aimsun_input_utils.\
        ControlJunctionType(generator_id % 5)
    default_control_junction.cycle = float(generator_id)
    default_control_junction.offset = float(generator_id)
    default_control_metering = aimsun_input_utils.ControlMetering()
    default_control_metering.control_metering_type = aimsun_input_utils.\
        ControlMeteringType(generator_id % 4)
    default_control_metering.metering_external_id = str(generator_id)
    # Generate and attributes
    attrs = [[] for _ in range(4)]
    for i in range(datasize):
        # Generate and save static Schedule data
        schedule_item = aimsun_input_utils.MasterControlPlanItem()
        schedule_item.control_plan_external_id = str(generator_id + i)
        schedule_item.duration = generator_id + i
        schedule_item.from_time = generator_id + i
        schedule_item.zone = generator_id
        attrs[0].append(schedule_item)
        # Generate and save static Metering data
        metering_item = aimsun_input_utils.Metering()
        metering_item.metering_type = aimsun_input_utils.MeteringType(
            generator_id % 5)
        metering_item.vehicle_flow = generator_id + i
        attrs[1].append(metering_item)
        # Generate and save static Detectors data
        detectors_item = aimsun_input_utils.Detector()
        detector_truth = bool(generator_id % 2)
        detectors_item.detect_count = detector_truth
        detectors_item.detect_density = not detector_truth
        detectors_item.detect_equipped_vehicles = detector_truth
        detectors_item.detect_headway = not detector_truth
        detectors_item.detect_occupancy = detector_truth
        detectors_item.detect_presence = not detector_truth
        detectors_item.detect_speed = not detector_truth
        detectors_item.extended_length = float(generator_id)
        detectors_item.number_of_lanes = generator_id % 5
        detectors_item.offset = float(generator_id)
        detectors_item.position_from_end = float(generator_id * 2)
        attrs[2].append(detectors_item)
        # Generate and save static ControlPlan data
        control_plan_item = aimsun_input_utils.ControlPlan()
        control_plan_item.control_junctions = [
            default_control_junction for _ in range(datasize)]
        control_plan_item.control_meterings = [
            default_control_metering for _ in range(datasize)]
        control_plan_item.offset = generator_id
        attrs[3].append(control_plan_item)
    # Assign static generated attributes to MasterControlPlan object
    mcp = aimsun_input_utils.MasterControlPlan()
    mcp.schedule, mcp.meterings, mcp.detectors, mcp.control_plans = tuple(attrs)
    mcp.external_id, mcp.name = str(generator_id), f'ControlPlan_{generator_id}'
    return mcp


def _create_section_slacs_object_from_filepath(
    filepath: str
) -> aimsun_input_utils.SectionSpeedLimitsAndCapacities:
    """Return a SectionSpeedLimitsAndCapacities given its file location.

    Args:
        filepath: Path to the file containing SectionSpeedLimitsAndCapacities.
    Returns:
        section_speed_limits_and_capacities: Created object from given filepath.
    """
    assert len(filepath) > 0
    return aimsun_input_utils.SectionSpeedLimitsAndCapacities(filepath)


def _create_static_section_slacs_object(
    num_sections: int, speed_limit_median: float, capacity_median: float
) -> aimsun_input_utils.SectionSpeedLimitsAndCapacities:
    """Create static SectionSpeedLimitsAndCapacities with given parameters.

    Args:
        num_sections: Number of road sections.
        speed_limit_median: Median of road section speed limits (km/h).
        capacity_median: Median of road section capacities (veh).
    Returns:
        sslacs_obj: SectionSpeedLimitsAndCapacities object with attributes
            defined by input parameters.
    """
    sslacs_obj = aimsun_input_utils.SectionSpeedLimitsAndCapacities()
    sslacs_obj.speed_limit_and_capacity_list = []
    for i in range(num_sections):
        sec_obj = aimsun_input_utils.SectionSpeedLimitAndCapacity()
        sec_obj.speed_limit_in_km_per_hour = speed_limit_median
        sec_obj.capacity_in_vehicles_per_hour = capacity_median
        sec_obj.section_internal_id = i
        sslacs_obj.speed_limit_and_capacity_list.append(sec_obj)
    return sslacs_obj


def _create_random_section_slacs_object(
    num_sections: int
) -> aimsun_input_utils.SectionSpeedLimitsAndCapacities:
    """Create a random SectionSpeedLimitsAndCapacities object with attributes
    defined by given parameters.

    Args:
        num_sections: Number of road sections.
    Returns:
        sslacs_obj: SectionSpeedLimitsAndCapacities object with attributes
            defined by input parameters.
    """
    sslacs_obj = aimsun_input_utils.SectionSpeedLimitsAndCapacities()
    sslacs_obj.speed_limit_and_capacity_list = []
    for _ in range(num_sections):
        sec_obj = aimsun_input_utils.SectionSpeedLimitAndCapacity()
        sec_obj.speed_limit_in_km_per_hour = (
            (random.random() - 0.5) * 20.0 + random.randint(20, 80))
        sec_obj.capacity_in_vehicles_per_hour = random.random() * 200.0
        sec_obj.section_internal_id = random.randint(0, 9999)
        sslacs_obj.speed_limit_and_capacity_list.append(sec_obj)
    return sslacs_obj


def _create_detectors(num_detectors: int) -> aimsun_input_utils.Detectors:
    """Generate Detectors instance for flow detector.

    This function is used to test the Detectors class in the context of flow
    detector in Aimsun. It randomly creates num_detectors detectors with
    detector external id and road section internal id.
    Args:
        num_detectors: Number of detectors in the Detectors class instance.
    Returns:
        detectors: Detectors object with the specified number of detectors.
    """
    detector_list = []
    for _ in range(num_detectors):
        detector = aimsun_input_utils.Detector()
        # Generate random detector_id
        random_detector_external_id = f"detector {random.randint(0, 9999)}"
        assert isinstance(random_detector_external_id, str)
        # Generate random section_id
        random_section_internal_id = random.randint(0, 9999)
        assert isinstance(random_section_internal_id, int)
        # Add random detector_id and section_id to detector_section_ids
        detector.external_id = random_detector_external_id
        detector.aimsun_section_internal_id = random_section_internal_id
        detector_list.append(detector)
    detectors = aimsun_input_utils.Detectors()
    detectors.detector_list = detector_list
    return detectors


def _create_traffic_management_strategy_from_filepath(
    filepath: str
) -> aimsun_input_utils.TrafficManagementStrategy:
    """Create a TrafficManagementStrategy object from given filepath.

    Args:
        filepath: Path to the file containing TrafficManagementStrategy object.
    Returns:
        traffic_management_strategy: Created object from given filepath.
    """
    assert len(filepath) > 0
    return aimsun_input_utils.TrafficManagementStrategy(filepath)


def _create_static_traffic_management_strategy_object(
    num_policies: int, num_scenario_changes: int, sc_type: int,
    external_id: str
) -> aimsun_input_utils.TrafficManagementStrategy:
    """Create a static TrafficManagementStrategy object with attributes defined
    by input parameters.

    Args:
        num_policies: Number of policies.
        num_scenario_changes: Number of scenario changes.
        sc_type: Type of scenario change.
        external_id: External ID of the object.
    Returns:
        tms_obj: TrafficManagementStrategy object with attributes defined by
            above input parameters.
    """
    tms_obj = aimsun_input_utils.TrafficManagementStrategy()
    tms_obj.external_id = external_id
    tms_obj.name = external_id
    tms_obj.policies = []
    for i in range(num_policies):
        policy = aimsun_input_utils.TrafficPolicy()
        policy.name = f"policy{i}"
        policy.external_id = f"policy_ext_id{i}"
        policy.scenario_changes = []
        for j in range(num_scenario_changes):
            tcc = aimsun_input_utils.TurningClosingChange()
            tcc.name = f"tcc{j}"
            tcc.external_id = f"tcc_ext_id{j}"
            tcc.destination_centroid_external_id = j + 1
            tcc.origin_centroid_external_id = j - 1
            tcc.scenario_change_type = sc_type
            policy.scenario_changes.append(tcc)
        tms_obj.policies.append(policy)
    return tms_obj


def _create_random_traffic_management_strategy_object(
    num_policies: int, num_scenario_changes: int
) -> aimsun_input_utils.TrafficManagementStrategy:
    """Create a random TrafficManagementStrategy object with attributes defined
    by input parameters.

    Args:
        num_policies: Number of policies.
        num_scenario_changes: Number of scenario changes.
    Returns:
        tms_obj: TrafficManagementStrategy object with attributes defined by
            above input parameters.
    """
    tms_obj = aimsun_input_utils.TrafficManagementStrategy()
    tms_obj.external_id = f"tms_ext_id{random.randint(0, 9999)}"
    tms_obj.name = "tms_name"
    tms_obj.policies = []
    for i in range(num_policies):
        policy = aimsun_input_utils.TrafficPolicy()
        policy.name = "policy" + str(i)
        policy.external_id = f"policy_ext_id{random.randint(0, 9999)}"
        policy.scenario_changes = []
        for j in range(num_scenario_changes):
            tcc = aimsun_input_utils.TurningClosingChange()
            tcc.name = f"tcc{j}"
            tcc.external_id = f"tcc_ext_id{random.randint(0, 9999)}"
            tcc.destination_centroid_external_id = random.randint(0, 9999)
            tcc.origin_centroid_external_id = random.randint(0, 9999)
            tcc.scenario_change_type = random.randint(0, 19)
            policy.scenario_changes.append(tcc)
        tms_obj.policies.append(policy)
    return tms_obj


def generate_random_external_id() -> str:
    """Generate a random ID for a detector"""
    random_id = f"detector_{random.randint(0, 9999)}"
    assert isinstance(random_id, str)
    return random_id


def _generate_random_datetime() -> datetime.datetime:
    """Generate a random datetime for a detector's flow data."""
    min_year = 1980
    max_year = 2021
    start = datetime.datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + datetime.timedelta(days=365 * years)
    random_datetime = start + (end - start) * random.random()
    assert isinstance(random_datetime, datetime.datetime)
    return random_datetime


def _generate_random_flowsize() -> float:
    """Generate a random flow size for a detector."""
    random_flowsize = round(random.uniform(0.0, 200.0), 3)
    assert isinstance(random_flowsize, float)
    return random_flowsize


def generate_random_flowdata() -> Dict[datetime.datetime, float]:
    """Generate a random flow data for a detector."""
    random_flowdata = {}
    datasize = random.randint(0, 100)
    for _ in range(datasize):
        timestamp = _generate_random_datetime()
        flowsize = _generate_random_flowsize()
        random_flowdata.update({timestamp: flowsize})
    assert isinstance(random_flowdata, dict)
    return random_flowdata


if __name__ == '__main__':
    unittest.main()
