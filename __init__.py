# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Watering class from file Watering.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .watering import QGISPlugin_WaterIng
    return QGISPlugin_WaterIng(iface)
