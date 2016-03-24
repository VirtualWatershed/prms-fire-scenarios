"""
PRMS Fire Modeling API

Date: Feb 25 2016
"""
from flask import jsonify, request, Response
from flask import current_app as app

import math
import json
import datetime

from . import api
from ..models import Scenario, Hydrograph, Inputs, Outputs
from util import propagate_all_vegetation_changes, get_veg_map_by_hru


@api.route('/api/scenarios/<scenario_id>', methods=['GET', 'DELETE'])
def scenario_by_id(scenario_id):
    """
    Look up or delete a scenario by its id
    """
    if request.method == 'GET':

        scenario = Scenario.objects(id=scenario_id).first()

        if scenario:
            return jsonify(scenario=scenario.to_json())

        else:
            return Response(
                json.dumps(
                    {'message': 'no scenario id found! ' +
                                'currently the scenario id must be 1 or 0!'}
                ), 400, mimetype='application/json'
            )

    if request.method == 'DELETE':

        scenario = Scenario.objects(id=scenario_id).first()

        if scenario:

            try:
                scenario.delete()
                return jsonify(
                    message='scenario with id ' + scenario_id + ' removed!'
                )

            except:
                return Response(
                    json.dumps(
                        {'message': 'error deleting scenario ' + scenario_id}

                    ), 400, mimetype='application/json'
                )

        else:

            return Response(
                json.dumps(
                    {'message': 'scenario_id' + scenario_id + 'not found'}
                ), 400, mimetype='application/json'
            )


@api.route('/api/scenarios', methods=['GET', 'POST'])
def scenarios():
    """
    Handle get and push requests for list of all finished scenarios and submit
    a new scenario, respectively.
    """
    if request.method == 'GET':

        scenarios = Scenario.objects

        # this is for the first three scenarios only
        if app.config['DEBUG'] and len(scenarios) < 3:
            #_init_dev_db(app.config['BASE_PARAMETER_NC'])
            for loop_counter in range(3):
                _init_dev_db(app.config['BASE_PARAMETER_NC'],loop_counter)

                scenarios = Scenario.objects


        return jsonify(scenarios=scenarios)

    else:
        BASE_PARAMETER_NC = app.config['BASE_PARAMETER_NC']

        # assemble parts of a new scenario record
        veg_map_by_hru = json.dumps(request.json['veg_map_by_hru'])

        name = request.json['name']

        time_received = datetime.datetime.now()

        updated_parameter_nc = propagate_all_vegetation_changes(
            BASE_PARAMETER_NC, veg_map_by_hru
        )

        updated_veg_map_by_hru = get_veg_map_by_hru(updated_parameter_nc)

        # TODO placeholder
        time_finished = datetime.datetime.now()

        # TODO placeholder
        inputs = Inputs()

        # TODO placeholder
        outputs = Outputs()

        # TODO placeholder
        hydrograph = Hydrograph(
            time_array=[datetime.datetime(2010, 10, 1, 0),
                        datetime.datetime(2010, 10, 1, 1),
                        datetime.datetime(2010, 10, 1, 2),
                        datetime.datetime(2010, 10, 1, 3)],
            streamflow_array=[24.4, 34.6, 10.0, 86.0]
        )

        new_scenario = Scenario(
            name=name,
            time_received=time_received,
            time_finished=time_finished,
            veg_map_by_hru=updated_veg_map_by_hru,
            inputs=inputs,
            outputs=outputs,
            hydrograph=hydrograph
        )

        new_scenario.save()

        return jsonify(scenario=new_scenario.to_json())


@api.route('/api/base-veg-map', methods=['GET'])
def hru_veg_json():
    if request.method == 'GET':
        """generate json file from netcdf file"""

        BASE_PARAMETER_NC = app.config['BASE_PARAMETER_NC']

        return jsonify(
            get_veg_map_by_hru(BASE_PARAMETER_NC)
        )


#def _init_dev_db(BASE_PARAMETER_NC):
def _init_dev_db(BASE_PARAMETER_NC, scenario_num=0):
    """

    """
    name = 'Demo development scenario' + str(scenario_num)
    time_received = datetime.datetime.now()

    updated_veg_map_by_hru = get_veg_map_by_hru(BASE_PARAMETER_NC)

    time_finished = datetime.datetime.now()

    inputs = Inputs()

    outputs = Outputs()

    # create two water years of fake data starting from 1 Oct 2010
    begin_date = datetime.datetime(2010, 10, 1, 0)
    time_array = [begin_date + datetime.timedelta(days=x) for x in
                  range(365*2)]

    # use simple exponentials as the prototype data
    x = range(365)
    streamflow_array = [pow(math.e, -pow(((i - 200.0 + 50*scenario_num)/100.0), 2)) for i in x]

    hydrograph = Hydrograph(
        time_array=time_array,
        streamflow_array=streamflow_array+streamflow_array
    )

    new_scenario = Scenario(
        name=name,
        time_received=time_received,
        time_finished=time_finished,
        veg_map_by_hru=updated_veg_map_by_hru,
        inputs=inputs,
        outputs=outputs,
        hydrograph=hydrograph
    )

    new_scenario.save()
