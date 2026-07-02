# Models package
# Import all models here so Flask-Migrate can detect them

from app.models.user import User                                    # noqa: F401
from app.models.role import Role                                    # noqa: F401
from app.models.user_role import UserRole                           # noqa: F401
from app.models.patient import Patient                              # noqa: F401
from app.models.medicine import Medicine                            # noqa: F401
from app.models.inventory import Inventory                          # noqa: F401
from app.models.visit import Visit                                  # noqa: F401
from app.models.prescription import Prescription                    # noqa: F401
from app.models.inventory_transaction import InventoryTransaction   # noqa: F401
from app.models.lab_test_catalog import LabTestCatalog              # noqa: F401
from app.models.laboratory import Laboratory                        # noqa: F401
from app.models.lab_report import LabReport                         # noqa: F401
from app.models.doctor_report import DoctorReport                   # noqa: F401
