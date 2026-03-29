"""QoS demo node demonstrating compatibility, incompatibility, and durability.

This module creates three publisher/subscriber pairs to illustrate
how Quality of Service policies affect message delivery:
  - Pair 1 (Compatible): RELIABLE pub -> BEST_EFFORT sub (works)
  - Pair 2 (Incompatible): BEST_EFFORT pub -> RELIABLE sub (silent failure)
  - Pair 3 (Durable): TRANSIENT_LOCAL pub -> delayed sub (cached delivery)
"""

from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"


class QoSDemoNode(Node):
    """A node with three pub/sub pairs demonstrating QoS behaviors."""

    def __init__(self, node_name: str):
        """Initialize three pub/sub pairs with different QoS profiles.

        Args:
            node_name (str): Name to register this node with in the ROS 2 graph.
        """
        super().__init__(node_name)

        # ── QoS profiles ────────────────────────────────────────
        reliable_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
        best_effort_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        transient_local_qos = QoSProfile(
            depth=5,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        # ── Pair 1: Compatible ──────────────────────────────────
        # RELIABLE pub + BEST_EFFORT sub = works
        # A BEST_EFFORT subscriber CAN connect to a RELIABLE publisher
        self._pub_compatible = self.create_publisher(
            String, "qos_compatible", reliable_qos
        )
        self._sub_compatible = self.create_subscription(
            String, "qos_compatible", self._compatible_cb, best_effort_qos
        )

        # ── Pair 2: Incompatible ────────────────────────────────
        # BEST_EFFORT pub + RELIABLE sub = silent failure
        # A RELIABLE subscriber CANNOT connect to a BEST_EFFORT publisher
        self._pub_incompatible = self.create_publisher(
            String, "qos_incompatible", best_effort_qos
        )
        self._sub_incompatible = self.create_subscription(
            String, "qos_incompatible", self._incompatible_cb, reliable_qos
        )

        # ── Pair 3: Transient Local durability ──────────────────
        # Publish 5 messages (one per second) before creating the subscriber.
        # With depth=5, the late-joining subscriber receives all cached messages.
        self._pub_durable = self.create_publisher(
            String, "qos_durable", transient_local_qos
        )

        # This attribute will be initialized later
        self._sub_durable = None
        self._durable_counter = 0
        self._durable_sub_created = False
        self._durable_qos = transient_local_qos
        self._durable_timer = self.create_timer(1.0, self._durable_publish_cb)

        # ── Periodic publisher for pairs 1 and 2 ────────────────
        self._counter = 0
        self._timer = self.create_timer(2.0, self._publish_cb)

        self.get_logger().info("QoS demo node started")
        self.get_logger().info(
            f"  {GREEN}[Compatible]{RESET}    RELIABLE pub -> BEST_EFFORT sub"
        )
        self.get_logger().info(
            f"  {RED}[Incompatible]{RESET}  BEST_EFFORT pub -> RELIABLE sub"
        )
        self.get_logger().info(
            f"  {CYAN}[Durable]{RESET}       TRANSIENT_LOCAL pub (5 msgs) -> delayed sub"
        )

    # ── Callbacks ───────────────────────────────────────────────

    def _publish_cb(self):
        """Publish a message on both the compatible and incompatible topics."""
        self._counter += 1
        msg = String()

        msg.data = f"compatible #{self._counter}"
        self._pub_compatible.publish(msg)
        self.get_logger().info(f"{GREEN}[Compatible]{RESET}    Published: '{msg.data}'")

        msg.data = f"incompatible #{self._counter}"
        self._pub_incompatible.publish(msg)
        self.get_logger().info(f"{RED}[Incompatible]{RESET}  Published: '{msg.data}'")

    def _compatible_cb(self, msg: String):
        """Handle messages from the compatible pair (this callback fires normally).

        Args:
            msg (String): The incoming message from the compatible topic.
        """
        self.get_logger().info(f"{GREEN}[Compatible]{RESET}    Received: '{msg.data}'")

    def _incompatible_cb(self, msg: String):
        """Handle messages from the incompatible pair (NEVER called due to QoS mismatch).

        Args:
            msg (String): The incoming message from the incompatible topic.
        """
        
        self.get_logger().info(f"{RED}[Incompatible]{RESET}  Received: '{msg.data}'")

    def _durable_publish_cb(self):
        """Publish numbered messages, then create a late-joining subscriber after 5."""
        self._durable_counter += 1
        msg = String()
        msg.data = f"durable #{self._durable_counter}"
        self._pub_durable.publish(msg)
        self.get_logger().info(f"{CYAN}[Durable]{RESET}       Published: '{msg.data}'")

        # After 5 messages, stop publishing and create the subscriber
        if self._durable_counter >= 5:
            self._durable_timer.cancel()
            self.get_logger().info(
                f"{CYAN}[Durable]{RESET}       Creating subscriber after 5 published msgs..."
            )
            self._sub_durable = self.create_subscription(
                String, "qos_durable", self._durable_cb, self._durable_qos
            )

    def _durable_cb(self, msg: String):
        """Handle cached messages delivered to the late-joining subscriber.

        Args:
            msg (String): A cached message from the durable topic.
        """

        self.get_logger().info(
            f"{CYAN}[Durable]{RESET}       Received cached: '{msg.data}'"
        )
