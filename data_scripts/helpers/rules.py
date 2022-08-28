"""
Rules Engine with Fluent Interface to applie business rules and transformations to a given record.   
"""

FARMERS_MARKET = "farmer's market"
SUPERMARKET = 'supermarket'
FRESH_ACCESS = 'fresh access'
CONVENIENCE_STORE = 'convenience store'
SUMMER_FOOOD = 'summer food site'
FOOD_BANK = 'food bank site'
GROW_PGH = 'grow pgh garden'
JUST_HARVEST_SOURCE = 'Just Harvest'


class RulesEngine(object):

    record: dict

    def __init__(self, record: dict) -> None:
        self.record = record

    def apply_global_rules(self):
        """
        Applies the gloabl rules for the initialized Record

        Returns:
            _type_: RulesEngine
        """

        if self.record['type'] == FARMERS_MARKET or self.record['type'] == SUPERMARKET or self.record['source_file'] == 'Just Harvest Fresh Corner Stores.xlsx':
            self.record['fresh_produce'] = True

        if self.record['source_file'] == 'Just Harvest - Fresh Access Markets.xlsx':
            self.record['food_bucks'] = True
            self.record['fresh_produce'] = True

        if self.record['source_file'] == 'Allegheny_County_WIC_Vendor_Locations.xlsx':
            self.record['wic'] = True

        if self.record['source_file'] == 'GPCFB - Green Grocer.xlsx' or self.record['type'] == FARMERS_MARKET:
            self.record['fmnp'] = True

        if self.record['source_file'] == 'Greater Pittsburgh Community Food Bank':
            self.record['free_distribution'] = True

        if self.record['source_file'] == 'PA.xlsx':
            self.record['food_bucks'] = True
            self.record['snap'] = True

        if self.record['type'] == 'summer food site':
            self.record['open_to_spec_group'] = 'children and teens 18 and younger'

        if self.record['food_bucks'] is True:
            self.record['snap'] = True

        if self.record['free_distribution']:
            self.record['snap'] = False
            self.record['wic'] = False
            self.record['fmnp'] = False
            self.record['food_bucks'] = False

        return self

    def apply_farmer_market_rules(self):
        """
        Applies the Farmer's Market Rules to the initialized Record.

        Returns:
            _type_: RulesEngine
        """

        if self.record.get('type', 'other') == FARMERS_MARKET:
            self.record['snap'] = True
            if 'green grocer' not in str(self.record['name']).lower():
                self.record['wic'] = True
            self.record['food_bucks'] = True
            self.record['fmnp'] = True
            self.record['free_distribution'] = False

        return self

    def apply_fresh_access_rules(self):
        """
        Applies the Fresh Access Rules to the initialized record.

        Returns:
            _type_: Rules Engine
        """
        if self.record['source_org'] == JUST_HARVEST_SOURCE:
            self.record['snap'] = True
            self.record['wic'] = True
            self.record['fmnp'] = True
            self.record['fresh_produce'] = True
            self.record['food_bucks'] = True
            self.record['free_distribution'] = False
        return self

    def apply_fresh_corners_rules(self):
        """
        Applies the Fresh Corners Rules to the initialized record.

        Returns:
            _type_: Rules Engine
        """
        if self.record['type'] == CONVENIENCE_STORE and self.record['snap'] is True:
            self.record['food_bucks'] = True
        self.record['fresh_produce'] = True

        return self

    def apply_bridgeway_rules(self):
        """                
        Applies the Bridgeway rules to the initialized record.

        Returns:
            _type_: Rules Engine
        """

        if 'fresh produce' in str(self.record.get('location_description', '')).lower():
            self.record['fresh_produce'] = True
        return self

    def apply_food_bank_rules(self):
        """
        Applies the Food Bank Rules to the initialized record.

        Returns:
            _type_: Rules Engine
        """

        if self.record['type'] == FOOD_BANK:
            self.record['snap'] = False
            self.record['wic'] = False
            self.record['fmnp'] = False
            self.record['food_bucks'] = False
            self.record['free_distribution'] = True

            desc = self.record.get('location_description', None)
            name = self.record.get('name', None)
            if (name or desc) and ('grocer' in str(desc).lower() or 'fresh' in str(desc).lower() or 'produce' in str(desc).lower() or 'green grocer' in str(name).lower()):
                self.record['fresh_produce'] = True

        return self

    def apply_summer_meal_rules(self):
        """
        Applies the Summer Meal Rules to the initialized record.

        Returns:
            _type_: Rules Engine
        """

        if self.record['type'] == SUMMER_FOOOD:
            self.record['snap'] = False
            self.record['wic'] = False
            self.record['fmnp'] = False
            self.record['food_bucks'] = False
            self.record['free_distribution'] = True
            self.record['open_to_spec_group'] = 'children and teens 18 and younger'
        return self

    def apply_grow_pgh_rules(self):
        """
        Applies the Grow PGH rules to the initialized record.

        Returns:
            _type_: Rules Engine
        """

        if self.record['type'] == GROW_PGH:
            self.record['snap'] = False
            self.record['wic'] = False
            self.record['fmnp'] = False
            self.record['fresh_produce'] = True
            self.record['food_bucks'] = False
            self.record['free_distribution'] = False

        return self

    def commit(self) -> dict:
        """
        Returns the record with the rules applied.

        Returns:
            dict: Updated Record
        """
        return self.record
